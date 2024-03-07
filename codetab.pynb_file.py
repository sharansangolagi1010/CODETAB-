#!/usr/bin/env python
# coding: utf-8

# 
# # DATA ANALYST ASSIGNMENT CODETAB

# # importing the libaries of python

# In[74]:


import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns


# # Reading the data 
# 

# # performing data cleaning

# In[75]:


order_report= pd.read_excel("Company X - Order Report.xlsx")
order_report.isnull().sum()
order_report=order_report.rename(columns={"ExternOrderNo":"Order ID"})


# In[76]:


order_report


# In[77]:


sku_master =pd.read_excel("Company X - SKU master.xlsx")
sku_master.isnull().sum()
sku_master["SKU"].unique() # The unique values in the SKU 
sku_master


# # performing data cleaning

# In[78]:


courier_invoice=pd.read_excel("Courier Company - Invoice.xlsx")
courier_invoice.isnull().sum() # there are no null values in the colum 
courier_invoice["Type of Shipment"].unique() # there are two unique values in the colum Type of Shipment
courier_invoice


# # courier data set 

# In[79]:


courier_rates=pd.read_excel("Courier Company - Rates.xlsx")
courier_rates


# In[80]:


pincode_zones= pd.read_excel("Company X - Pincode Zones.xlsx")
pincode_zones.isnull().sum()
pincode_zones


# In[81]:


data1=pd.merge(order_report,courier_invoice,on="Order ID", how="inner")
data2=pd.merge(data1,sku_master,on="SKU", how="inner")


# In[82]:


data1.drop_duplicates()


# In[83]:


data2.drop_duplicates()
data2["Order ID"].unique()


# In[84]:


data5 = data2.groupby("Order ID")["Weight (g)"].sum().reset_index(name="Total_weight (g)")
data5["AWB Code"]=data1["AWB Code"]
data5


# In[ ]:





# In[ ]:





# # converting the data courier_rates["Zone"] to small alphabet characther 

# In[85]:


def name(n):
    result = ""
    for i in n:
        if i == "A":
            result += "a"
        elif i == "B":
            result += "b"
        elif i == "C":
            result += "c"
        elif i == "D":
            result += "d"
        else:
            result += "e"
    return result


# In[86]:


courier_rates["Zone"]=courier_rates["Zone"].apply(name)
courier_rates


# # joining the tabels of  courier_rates and Data2

# In[87]:


new_data =pd.merge(courier_rates,data2,on="Zone",how="right")


# In[ ]:





# # droping the duplicates  

# In[88]:


new_data.drop_duplicates()
new_data.isnull().sum()
new_data


# # performing the data maluplation on the basics of the type of shipment 

# In[89]:


import numpy as np

new_data["new column"] = np.where(
    new_data["Type of Shipment"] == "Forward charges",
    new_data["Forward Fixed Charge"] + new_data["Forward Additional Weight Slab Charge"],
    np.where(
        new_data["Type of Shipment"] == "Forward and RTO charges",
        new_data["Forward Fixed Charge"]
        + new_data["Forward Additional Weight Slab Charge"]
        + new_data["RTO Additional Weight Slab Charge"],
                np.nan  
    )
)


# # droping the weight slabs column

# In[90]:


new_data=new_data.drop("Weight Slabs",axis=1)


# # performing the data manuplation for the weight slabs charges coloum 

# In[91]:


import numpy as np

new_data["weight_slab_charges"] = np.where(
    new_data["Type of Shipment"] == "Forward charges",new_data["Forward Additional Weight Slab Charge"],
    np.where(
        new_data["Type of Shipment"] == "Forward and RTO charges",new_data["Forward Additional Weight Slab Charge"]
        + new_data["RTO Additional Weight Slab Charge"],
                np.nan  
    )
)


# # renaming the all columns to the specific requirment 

# In[92]:


new_data=new_data.rename(columns={"Weight (g)":"Total weight as per Courier Company (G)",
                                  "new column":"Delivery Zone charged by Courier Company",
                                  "Zone":"Delivery Zone as per X",
                                  "weight_slab_charges":"Weight slab charged by Courier Company (KG)",
                                "Billing Amount (Rs.)":"Expected Charge as per X (Rs.)",})


# In[ ]:





# In[93]:


new_data


# # adding the expected charges and weight slab charges to get the charges billed by courier

# In[94]:


new_data["Charges Billed by Courier Company (Rs.)"]= new_data["Expected Charge as per X (Rs.)"] + new_data["Weight slab charged by Courier Company (KG)"]


# # charged courier bill = order qty * charged courier bill (Number of order qty multiplied by  courier bill )

# In[95]:


new_data["Charges Billed by Courier Company (Rs.)"]=new_data["Charges Billed by Courier Company (Rs.)"] * new_data["Order Qty"]


# # code to get the Difference Between Expected Charges and Billed Charges 

# In[96]:


new_data["Difference Between Expected Charges and Billed Charges (Rs.)"]=new_data["Charges Billed by Courier Company (Rs.)"]-new_data["Expected Charge as per X (Rs.)"]


# In[97]:


new_data=new_data.rename(columns={"Weight (g)":"Total weight as per Courier Company (G)",
                                  "new column":"Delivery Zone charged by Courier Company",
                                  "Zone":"Delivery Zone as per X",
                                  "weight_slab_charges":"Weight slab charged by Courier Company (KG)",
                                "Billing Amount (Rs.)":"Expected Charge as per X (Rs.)","Charged Weight":"Weight slab as per X (KG)"})


# In[ ]:





# # converting the total weight (g) to (KG)

# In[98]:


new_data["Total weight as per Courier Company (G)"]=new_data["Total weight as per Courier Company (G)"]*10**-3


# In[99]:


new_data=new_data.drop_duplicates()


# # droping the unwanted column where the not mentioned in the result sheet 

# In[100]:


new_data=new_data.drop(columns=["Forward Fixed Charge","Forward Additional Weight Slab Charge","RTO Fixed Charge","RTO Additional Weight Slab Charge","SKU","Warehouse Pincode","Customer Pincode","Type of Shipment","Order Qty"])


# # FINAL DATA SET 

# In[102]:


new_data


# In[113]:


new_data.to_excel('LHS_data.xlsx', index=False)


# In[114]:


#RHS data set 


# In[115]:


import numpy as np

new_data["Total_orders"] = np.where(
    new_data["Difference Between Expected Charges and Billed Charges (Rs.)"] == new_data["Weight slab charged by Courier Company (KG)"] ,
    "Correctly Charged",
    np.where(
        new_data["Difference Between Expected Charges and Billed Charges (Rs.)"] > new_data["Weight slab charged by Courier Company (KG)"],
        "Overcharged",
        np.where(
            new_data["Difference Between Expected Charges and Billed Charges (Rs.)"] < new_data["Weight slab charged by Courier Company (KG)"],
            "Undercharged",
            np.nan
        )
    )
)




# In[116]:


new_data


# In[117]:


new_data.head()


# In[118]:


new_data["amount"]=new_data["Difference Between Expected Charges and Billed Charges (Rs.)"]-new_data["Weight slab charged by Courier Company (KG)"]
new_data


# In[ ]:





# In[119]:


final_data=new_data.groupby("Total_orders")["amount"].value_counts()
final_data


# In[120]:


final_data_df = final_data.reset_index(name='count')
final_data_df


# In[121]:


final_data_df.to_excel('RHS_data.xlsx', index=False)


# In[ ]:





# In[ ]:





# In[ ]:




