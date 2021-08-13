import dash
from dash_html_components.Br import Br
from dash_html_components.H6 import H6
from flask import Flask
import dash_table
import math
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from pandas_datareader import data as web
from datetime import datetime as dt
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from IPython.core.display import display,HTML
dfA=pd.read_excel(r'C:\SLOTTING_TOOL\Export\ABC_8.xlsx')
dfs= pd.read_excel (r'D:\OE\StockOnHand_2810.xlsx')
datafilter = dfs.loc[dfs['StorageBin'].str.len() == 12].reset_index()
datafilter = datafilter.rename(columns={"StorageCondition":"WarehouseStorageCondition"})
datafilter = datafilter.rename(columns={"StorageBin":"BinType"})
datafilter = datafilter.rename(columns={"MaterialGroup":"ProductType"})
selection=datafilter[datafilter['StorageUOM'].str.contains('Pallet')]
selection1=selection.groupby(['WarehouseStorageCondition','StorageUOM','ProductType','Pallet'])[['Batch']].count().reset_index()
selection1.set_index(['WarehouseStorageCondition','ProductType'],inplace=True)
selection1['%'] = (100*selection1['Batch']/selection1['Batch'].sum(level ='ProductType')).round(2)
b1=selection1.reset_index()
bn=b1.groupby(['WarehouseStorageCondition','StorageUOM','ProductType','Batch'])[['Pallet']].count().reset_index()
bn.set_index(['WarehouseStorageCondition','ProductType'],inplace=True)
bn['%'] = (100*bn['Pallet']/bn['Pallet'].sum(level = 'ProductType')).round(2)
# bn.drop(bn[(bn.Ba
# tch==0)].index)
bx=bn.reset_index()
bm=bx.drop(bx[(bx.Batch==0)].index)
# print(bm)
bx=bm[bm['Batch'] == 1]
b3=bx.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b3= b3.rename(columns={"%":"Pallet/batch=1 %"})
bx2=bm[bm['Batch'] ==2 ]
b4=bx2.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b4= b4.rename(columns={"%":"Pallet/batch=2 %"})
bx3=bm[bm['Batch'] ==3 ]
b5=bx3.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b5= b5.rename(columns={"%":"Pallet/batch=3 %"})
bx4=bm[bm['Batch'] ==4 ]
b6=bx4.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b6= b6.rename(columns={"%":"Pallet/batch=4 %"})
bm1=pd.merge(b3,b4,how='outer')
bm2=pd.merge(bm1,b5,how='outer')
bm3=pd.merge(bm2,b6,how='outer')
all_pt = bm.ProductType.unique()
# print(all_pt)

spt1=datafilter[datafilter['StorageUOM'].str.contains('Pallet') & datafilter['WarehouseStorageCondition'].str.contains('AC')]
sptAP=spt1.groupby(['WarehouseStorageCondition','StorageUOM','ProductType'])[['Pallet']].count().reset_index()
spt2=datafilter[datafilter['StorageUOM'].str.contains('Pallet') & datafilter['WarehouseStorageCondition'].str.contains('CO')]
sptCP=spt2.groupby(['WarehouseStorageCondition','StorageUOM','ProductType'])[['Pallet']].count().reset_index()
spt3=datafilter[datafilter['StorageUOM'].str.contains('Pallet') & datafilter['WarehouseStorageCondition'].str.contains('FZ')]
sptFP=spt3.groupby(['WarehouseStorageCondition','StorageUOM','ProductType'])[['Pallet']].count().reset_index()
spt4=datafilter[datafilter['StorageUOM'].str.contains('Bin') & datafilter['WarehouseStorageCondition'].str.contains('AC')]
sptAB=spt4.groupby(['WarehouseStorageCondition','StorageUOM','ProductType'])[['Carton']].count().reset_index()
spt5=datafilter[datafilter['StorageUOM'].str.contains('Bin') & datafilter['WarehouseStorageCondition'].str.contains('CO')]
sptCB=spt5.groupby(['WarehouseStorageCondition','StorageUOM','ProductType'])[['Carton']].count().reset_index()
spt6=datafilter[datafilter['StorageUOM'].str.contains('Bin') & datafilter['WarehouseStorageCondition'].str.contains('FZ')]
sptFB=spt6.groupby(['WarehouseStorageCondition','StorageUOM','ProductType'])[['Carton']].count().reset_index()
m1=pd.merge(sptAP,sptCP,how='outer')
m2=pd.merge(m1,sptFP,how='outer')
m2=m2.rename(columns={"Pallet":"Quantity"})
m3=pd.merge(sptAB,sptCB,how='outer')
m4=pd.merge(m3,sptFB,how='outer')
m4=m4.rename(columns={"Carton":"Quantity"})
spt=pd.merge(m2,m4,how='outer')
def growth(row):
    if row["WarehouseStorageCondition"] in["AC","Aircon"] and row["ProductType"]in["Pharma","Pharma Ethical","Animal Health Drug"]:
        rate=1.05
        q=row["Quantity"]*rate
    elif row["WarehouseStorageCondition"] in["CO","Cold Room"] and row["ProductType"]in["Pharma","Pharma Ethical"]:
        rate=1.08
        q=row["Quantity"]*rate
    elif row["WarehouseStorageCondition"] in["AC","Aircon"] and row["ProductType"]in["Consumer Healthcare"]:
        rate=1.08
        q=row["Quantity"]*rate
    elif row["WarehouseStorageCondition"] in["CO","Cold Room"] and row["ProductType"]in["Consumer Healthcare"]:
        rate=1.03
        q=row["Quantity"]*rate
    elif row["WarehouseStorageCondition"] in["AC","Aircon"] and row["ProductType"]in["Medical Devices","MDD"]:
        rate=1.08
        q=row["Quantity"]*rate
    elif row["WarehouseStorageCondition"] in["CO","Cold Room"] and row["ProductType"]in["Medical Devices","MDD","Consumer Healthcare"]:
        rate=1.03
        q=row["Quantity"]*rate
    elif row["WarehouseStorageCondition"] in["FZ","Freezer"]:
        rate=1.05
        q=row["Quantity"]*rate
    else:
        rate=1.05
        q=row["Quantity"]*rate
    return q
spt['2022'] = spt.apply(lambda row: int(growth(row)), axis=1)
spt['2023'] = spt.apply(lambda x:  int(x['2022']*1.05), axis=1)
spt['2024'] = spt.apply(lambda x:  int(x['2023']*1.05), axis=1)
spt['2025'] = spt.apply(lambda x:  int(x['2024']*1.05), axis=1)
spt['2026'] = spt.apply(lambda x:  int(x['2025']*1.05), axis=1)
spt['2027'] = spt.apply(lambda x:  int(x['2026']*1.05), axis=1)
spt['2028'] = spt.apply(lambda x:  int(x['2027']*1.05), axis=1)
spt['2029'] = spt.apply(lambda x:  int(x['2028']*1.05), axis=1)
spt['2030'] = spt.apply(lambda x:  int(x['2029']*1.05), axis=1)
spt=spt.rename(columns={'Quantity':'Pallet Quantity'})
# print(spt)
pr=datafilter.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['Material']].nunique().reset_index()
# bq=bm[bm['Batch'] > 1]
# b3=bq.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
# b3= b3.rename(columns={"%":"NoPalletsperBatch=2 %"})
df7 = pd.read_csv (r'D:\OE\2810_June_Complete1.csv')
df7.columns = df7.columns.str.replace(' ', '')
df7 = df7.rename(columns={"StorageCondition":"WarehouseStorageCondition"})
df7 = df7.drop(df7[(df7.WarehouseStorageCondition==0)].index)
df7 = df7.drop(df7[(df7.Quantity==0)].index)
df7['PAL'] = df7.apply(lambda x: int(x[16] / x[17]) , axis=1)
df7['CAR'] = df7.apply(lambda x: int(x[16] / x[18]) , axis=1)
#  x if (x < 30 or x > 60) else 0
df7['PAL_QTY'] = df7.apply(lambda x: x[16] // x[19] , axis=1)
df7['LOS_QTY'] = df7.apply(lambda x: x[16] % x[20], axis=1)
# # # OUT_QTY: ([QTY]-[LOS_QTY]-([PAL_QTY]*[PAL]))/[CAR]
# # df7 = df7.fillna(0)
df7['OUT_QTY'] = df7.apply(lambda x: (x[16]-x[22]-(x[21])*x[19])/x[20], axis=1)
df7.loc[df7['LOS_QTY'] > 0, 'Los_FREQ'] = 1
df7.loc[df7['PAL_QTY'] > 0, 'PAL_FREQ'] = 1
df7.loc[df7['OUT_QTY'] > 0, 'OUT_FREQ'] = 1
df7 = df7.fillna(0)
# print(df7)
df7 = df7.groupby(["WarehouseStorageCondition","MaterialGroup"]).apply(lambda s: pd.Series({ 
    "LosSum": s["Los_FREQ"].sum(), 
    "OutSum": s["OUT_FREQ"].sum(), 
    "PalSum": s["PAL_FREQ"].sum(), 
}))
# print(df7)
df7['TotalFreq'] =df7.apply(lambda x: x[1] + x[0] + x[2], axis=1)
df7['LOS%'] =df7.apply(lambda x: x[0]/x[3]*100, axis=1).round(decimals=0)
df7['OUT%'] =df7.apply(lambda x: x[1]/x[3]*100, axis=1).round(decimals=0)
df7['PAL%'] =df7.apply(lambda x: x[2]/x[3]*100, axis=1).round(decimals=0)
df7=df7.reset_index()
df7 = df7.rename(columns={"MaterialGroup":"ProductType"})
df7=df7.drop(df7[(df7.WarehouseStorageCondition==0)].index)

orderprofile=df7[['WarehouseStorageCondition','ProductType','LOS%','OUT%','PAL%']]

merge=pd.merge(bm3,pr,how='inner')
merge=merge.rename(columns={"Material":"ProductRange"})
p_inner=pd.merge(m2,merge,how='inner')
p_inner = p_inner.fillna(0)
c_inner1=pd.merge(m4,pr,how='inner')
c_inner=pd.merge(c_inner1,orderprofile,how="inner")
c_inner = c_inner.fillna(0)
c_inner=c_inner.rename(columns={"Material":"ProductRange"})
# print(c_inner)


def sys1(row):
    if row["Pallet/batch=2 %"] <30:
        if row['WarehouseStorageCondition']in["AC","NAC", "CO", "FZ"]:
            
            if row['Quantity']<2:
                v1=1
            elif row['Quantity']<3:
                v1=2
            else:
                v1=3
            if row['ProductRange']<540:
                v3=1
            else:
                v3=2
            if row['Pallet/batch=2 %']<30:
                v4=1
            else:
                v4=0

            sys1 = v1+v4+v3
        else:
            sys1=0
    else:
        sys1=0
    return sys1
p_inner['Selective Pallet Racking (SPR)'] = p_inner.apply(lambda row: sys1(row), axis=1)

def sys2(row):
    if row['WarehouseStorageCondition']in["AC","NAC", "CO"] :
        if row['Quantity']<3:
            v1=1
        elif row['Quantity']<5:
            v1=2
        else:
            v1=3
        if row['ProductRange']<540:
            v3=1
        else:
            v3=2
        if row['Pallet/batch=2 %']<50:
            v4=1
        else:
            v4=0
        sys2 = v1+v3+v4
        
    else:
        sys2=0
    return sys2
p_inner['Very Narrow Ailse (VNA) & Truck'] =p_inner.apply(lambda row: sys2(row), axis=1)
# df1.head()
def sys4(row):
    if row['WarehouseStorageCondition']in["AC","NAC", "CO"]:
        if row['Quantity']<3:
            v1=1
        elif row['Quantity']<5:
            v1=2
        else:
            v1=3
        if row['ProductRange']<540:
            v3=1
        else:
            v3=2
        if row['Pallet/batch=2 %']<50:
            v4=1
        else:
            v4=0
        sys4 = v1+v3+v4 
        
    else:
        sys4=0
    return sys4
p_inner['Automatic Storage Retrieval System (ASRS)'] =p_inner.apply(lambda row: sys4(row), axis=1)
# df1.head()
def sys5(row):
    if row["Pallet/batch=2 %"] >30:

        if row['WarehouseStorageCondition']in["AC","NAC", "CO","FZ"]:
            if row['Quantity']<6 and row['Quantity']>2:
                v1=1
            elif row['Quantity']<10:
                v1=2
            else:
                v1=3
            if row['ProductRange']<540:
                v3=1
            else:
                v3=2
            sys5 = v1+v3+2
        else:
            sys5=0
    else:
        sys5=0
    return sys5
p_inner['Double Deep Racking (DDR)'] = p_inner.apply(lambda row: sys5(row), axis=1)
# df1.head()
def sys6(row):
    if row['WarehouseStorageCondition']in["AC","NAC", "CO","FZ"]:
        if row['Quantity']<1000:
            v1=3
        else:
            v1=1
        if row['ProductRange']<540:
            v3=1
        else:
            v3=2
        if row['Pallet/batch=2 %']<50:
            v4=1
        else:
            v4=0
        sys6= v1+v3+v4  
        
    else:
        sys6=0
    return sys6
p_inner['Ground Storage'] =p_inner.apply(lambda row: sys6(row), axis=1)
# df1.head()
def sys7(row):
    if row["Pallet/batch=4 %"] >30:
        if row['WarehouseStorageCondition']in["AC","NAC", "CO"]:
            if row['Quantity']<1000000 and row['Quantity']>10:
                v1=1
            elif row['Quantity']<10 and row['Quantity']>5:
                v1=2
            elif row['Quantity']<5:
                v1=3
            else:
                v1=0
            if row['ProductRange']<540:
                v3=1
            else:
                v3=2
            sys7 =v1+v3+2 
        else:
            sys7=0
    else:
        sys7=0
    return sys7
p_inner['Drive-Through Rack'] = p_inner.apply(lambda row: sys7(row), axis=1)
# df1.head()
def sys9(row):
    if row["Pallet/batch=4 %"] >30:
        if row['WarehouseStorageCondition']in["AC","NAC", "CO"] :
            if row['Quantity']<1000000 and row['Quantity']>10:
                v1=1
            elif row['Quantity']<10 and row['Quantity']>5:
                v1=2
            elif row['Quantity']<5:
                v1=3
            else:
                v1=0
            if row['ProductRange']<540:
                v3=1
            else:
                v3=2

            sys9 =v1+v3+2
        else:
            sys9=0
    else:
        sys9=0
    return sys9
p_inner['Drive-In Rack'] = p_inner.apply(lambda row: sys9(row), axis=1)

def sys8(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO"]:
        if row['Quantity']<3 and row['Quantity']>1:
            v1=1
        elif row['Quantity']<5 and row['Quantity']>3:
            v1=2
        elif row['Quantity']<5:
            v1=3
        else:
            v1=0
        if row['ProductRange']<100000 and row['ProductRange']>1300:
            v3=1
        else:
            v3=2
        if row['Pallet/batch=2 %']<50:
            v4=1
        else:
            v4=0
        sys8 = v1+v3+v4  
        
    else:
        sys8=0
    return sys8
p_inner['Shuttle Storage System'] = p_inner.apply(lambda row: sys8(row), axis=1)
# df1.head()

def sys11(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO"]:
        if row['Quantity']<3 and row['Quantity']>1:
            v1=1
        elif row['Quantity']<=5 and row['Quantity']>=3:
            v1=2
        elif row['Quantity']>0:
            v1=3
        else:
            v1=0
        if row['ProductRange']<540:
            v3=1
        else:
            v3=2
        if row['Pallet/batch=2 %']>50:
            v4=2
        else:
            v4=0
        sys11 = v1+v3+v4
        
    else:
        sys11=0
    return sys11
p_inner['Mobile Rack'] = p_inner.apply(lambda row: sys11(row), axis=1)
# m2.head(30)
def sys12(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO"]:
        if row['Quantity']>10000:
            v1=3
        else:
            v1=0
        if row['ProductRange']<100000 and row['ProductRange']>1300:
            v3=1
        else:
            v3=2
        if row['Pallet/batch=2 %']<50:
            v4=1
        else:
            v4=0
        sys11 = v1+v3+v4
        
    else:
        sys11=0
    return sys11
p_inner['High Bay Pallet Rack'] = p_inner.apply(lambda row: sys12(row), axis=1)
# m2.head(30)

result_p=p_inner.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]]  
# print(result_p)
def sys13(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO",'FZ'] :
        if row['Quantity']<0.5:
            v1=1
        elif row['Quantity']<=1:
            v1=2
        elif row['Quantity']>1:
            v1=3
        else:
            v1=0
        if row['ProductRange']<540:
            v3=1
        elif row['ProductRange']>540:
            v3=2
        else:
            v3=0
        sys14 = v1+v3
        
    else:
        sys14=0
    return sys14
c_inner['Flow Rack'] = c_inner.apply(lambda row: sys13(row), axis=1)

def sys14(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO",'FZ'] :
        if row['Quantity']<0.5:
            v1=1
        elif row['Quantity']<=1:
            v1=2
        elif row['Quantity']>1:
            v1=3
        else:
            v1=0
        if row['ProductRange']<540:
            v3=1
        elif row['ProductRange']>540:
            v3=2
        else:
            v3=0
        sys14 = v1+v3
        
    else:
        sys14=0
    return sys14
c_inner['Shelf Rack'] = c_inner.apply(lambda row: sys14(row), axis=1)
# # df1.head()

def sys15(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO",'FZ']:
        if row['Quantity']<0.5:
            v1=1
        elif row['Quantity']<=1:
            v1=2
        elif row['Quantity']>1:
            v1=3
        else:
            v1=0
        if row['ProductRange']<540:
            v3=1
        elif row['ProductRange']>540:
            v3=2
        sys15 = v1+v3  
        
    else:
        sys15=0
    return sys15
c_inner['High Bay Shelf Rack'] = c_inner.apply(lambda row: sys15(row), axis=1)
def sys16(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO",'FZ']:
        if row['Quantity']<0.5:
            v1=1
        elif row['Quantity']<=1:
            v1=2
        elif row['Quantity']>1:
            v1=3
        else:
            v1=0
        if row['ProductRange']<540:
            v3=1
        elif row['ProductRange']>540:
            v3=2
        else:
            v3=0
        sys16 = v1+v3  
        
    else:
        sys16=0
    return sys16
c_inner['Bin Rack'] =c_inner.apply(lambda row: sys16(row), axis=1)
# # df1.head()
def sys17(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO",'FZ']:
        if row['Quantity']<0.5:
            v1=1
        elif row['Quantity']<=1:
            v1=2
        elif row['Quantity']>1:
            v1=3
        else:
            v1=0
        if row['ProductRange']<540:
            v3=1
        elif row['ProductRange']>540:
            v3=2
        else:
            v3=0
        sys17 = v1+v3 
        
    else:
        sys17=0
    return sys17
c_inner['Mobile Shelving'] = c_inner.apply(lambda row: sys17(row), axis=1)

def sys18(row):
    if row['WarehouseStorageCondition']in["AC","NAC","CO",'FZ']:
        if row['Quantity']<0.5:
            v1=1
        elif row['Quantity']<=1:
            v1=2
        elif row['Quantity']>1:
            v1=3
        else:
            v1=0
        if row['ProductRange']>0:
            v3=1
        else:
            v3=0
        sys18 = v1+v3 
        
    else:
        sys18=0
    return sys18
c_inner['Vertical Carousel Storage'] = c_inner.apply(lambda row: sys18(row), axis=1)

result_b=c_inner.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11,12,13]] 
# print(result_b)
grouped = result_p.groupby(result_p.WarehouseStorageCondition)
result_p_AC = grouped.get_group("AC")
grouped = result_p.groupby(result_p.WarehouseStorageCondition)
result_p_CO = grouped.get_group("CO")


group1 = result_b.groupby(result_b.WarehouseStorageCondition)
result_b_AC = group1.get_group("AC")
group2 = result_b.groupby(result_b.WarehouseStorageCondition)
result_b_CO = group2.get_group("CO")
group3 = result_b.groupby(result_b.WarehouseStorageCondition)
result_b_FZ = group3.get_group("FZ")

t0=result_p_AC.sort_values(by='Quantity', ascending=False)
# print(t0)
t1=t0.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]] 
t1=t1.rename(columns={"Quantity":"Pallet Quantity"})
dfx=t1.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
dfx['Recommend System 1']=dfx.idxmax(axis=1)
dfx=dfx.reset_index()
dfx=dfx.iloc[:,[0,1,2,3,4,5,15]] 
# sum_area=dfx
##recommend 2
r2=t0.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]]
r2=r2.rename(columns={"Quantity":"Pallet Quantity"})
dfx2=r2.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
dfx3=dfx2.drop(['Selective Pallet Racking (SPR)'], axis = 1)
dfx3['Recommend System 2']=dfx3.idxmax(axis=1)

dfx3=dfx3.reset_index()
dfx3=dfx3.iloc[:,[0,1,2,3,4,5,14]] 
## recommend 3
r3=t0.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]]
r3=r3.rename(columns={"Quantity":"Pallet Quantity"})
dfx4=r3.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
dfx5=dfx4.drop(['Selective Pallet Racking (SPR)'], axis = 1)
dfx5=dfx5.drop(['Very Narrow Ailse (VNA) & Truck'], axis = 1)
dfx5=dfx5.drop(['Ground Storage'], axis = 1)
dfx5['Recommend System 3']=dfx5.idxmax(axis=1)

dfx5=dfx5.reset_index()
dfx5=dfx5.iloc[:,[0,1,2,3,4,5,12]] 

# def showimage(row):
#     if row["Recommend System 1"]in['Selective Pallet Racking (SPR)'] :
#         image='https://portalimages.blob.core.windows.net/thumbnails/images/p52olmr5_1-375x300.jpg'
#     elif row["Recommend System 1"]in['Very Narrow Ailse (VNA) & Truck'] :
#         image='https://racksystemsinc.com/wp-content/uploads/2016/07/very-narrow-aisle-pallet-racking-01.jpg'
#     elif row["Recommend System 1"]in['Automatic Storage Retrieval System (ASRS)'] :
#         image='https://interlakemecalux.cdnwm.com/automated-storage-retrieval-systems/stacker-cranes-for-boxes/img1.1.2.jpg'
#     elif row["Recommend System 1"]in['Double Deep Racking (DDR)'] :
#         image='https://tse1.mm.bing.net/th?id=OIP.YYI3VqhYNhPvDbIlXvPjDAHaFG&pid=Api&P=0&w=244&h=169'
#     elif row["Recommend System 1"]in['Ground Storage'] :
#         image='https://racksystemsinc.com/wp-content/uploads/2016/07/very-narrow-aisle-pallet-racking-01.jpg'
#     elif row["Recommend System 1"]in['Drive-Through Rack'] :
#         image='https://tse1.mm.bing.net/th?id=OIP.w5jetxPxJGmo0d0WdRvNewHaFP&pid=Api&P=0&w=254&h=180'
#     elif row["Recommend System 1"]in['Drive-In Rack']:
#         image='https://www.cbmsystem.com/assets/images/racking/drive-in-rack-1.jpg'
#     elif row["Recommend System 1"]in['Shuttle Storage System']:
#         image='https://tse2.mm.bing.net/th?id=OIP.H-6WJBU3bKrl010TQ54N_QHaHD&pid=Api&P=0&w=172&h=165'
#     elif row["Recommend System 1"]in['Shuttle Storage System'] :
#         image='https://tse2.mm.bing.net/th?id=OIP.H-6WJBU3bKrl010TQ54N_QHaHD&pid=Api&P=0&w=172&h=165'
#     elif row["Recommend System 1"]in['Mobile Rack'] :
#         image='https://www.ssi-schaefer.com/resource/image/55454/landscape_ratio3x2/1141/759/fe151f4b3c10b588716599f1bf5edde8/xW/mobile-rack-reference-bankok-seafood-dam-image-en-2129-.jpg'
#     else:
#         image=''
#     return image
# dfx['image'] = dfx.apply(lambda row: showimage(row), axis=1)
# dfx3['image'] = dfx3.apply(lambda row: showimage(row), axis=1)
# def requireArea(row):
#     if row["Recommend System 1"]in['Selective Pallet Racking (SPR)'] :
#         wh_height=12
#         wh_length=100
#         p_height=1.8
#         p_width=0.8
#         p_length=1.2
#         aisle=4
#         level=wh_height //(p_height+0.4)
#         onebay=level*3
#         num=(wh_length-0.3)//2.8
#         sum_1=num*level*3
#         if row["Pallet Quantity"] <= onebay:
#             area=2.7*0.8
#         elif row["Pallet Quantity"]<= sum_1:
#             num2=int(row["Pallet Quantity"]/onebay)
#             area=num2*2.7*0.8
#         elif row["Pallet Quantity"]> sum_1: 
#             no_bay=row["Pallet Quantity"]//sum_1
#             lef=row["Pallet Quantity"]%sum_1
#             if no_bay<2:
#                 area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
#             else:
#                 area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
#     elif row["Recommend System 1"]in['Shelf Rack']:
#         wh_length=100
#         c_height=0.5
#         c_width=0.3
#         c_length=0.4
#         aisle=3
#         level=4
#         s_depth=1.7
#         bay=1.28
#         num1=bay//c_length
#         num2=s_depth//c_width
#         sum_1=num1*num2*4
#         bay_line=(wh_length-0.3)//bay
#         no_bay=int(row["Bin Quantity"]//sum_1+1)
#         line=int(no_bay//bay_line+1)
#         if row["Bin Quantity"] <sum_1:
#             area=math.ceil(bay*s_depth)
#         elif row["Bin Quantity"] < bay_line*sum_1:
#             area=math.ceil(no_bay*bay*s_depth)
#         else:
#             area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
#     else:
#         area=0
#     return area
# dfx['Area(sqm)'] = dfx.apply(lambda row: int(requireArea(row)) , axis=1)


# print(dfpal)
# def requireArea2(row):
#     if row["Recommend System 2"]in['Very Narrow Ailse (VNA) & Truck'] :
#         wh_height=12
#         wh_length=100
#         p_height=1.8
#         p_width=0.8
#         p_length=1.2
#         aisle=2.8
#         level=wh_height //(p_height+0.4)
#         onebay=level*3
#         num=(wh_length-0.3)//2.8
#         sum_1=num*level*3
#         if row["Pallet Quantity"] <= onebay:
#             area=2.7*0.8
#         elif row["Pallet Quantity"]<= sum_1:
#             num2=int(row["Pallet Quantity"]/onebay)
#             area=num2*2.7*0.8
#         elif row["Pallet Quantity"]> sum_1: 
#             no_bay=row["Pallet Quantity"]//sum_1
#             lef=row["Pallet Quantity"]%sum_1
#             if no_bay<2:
#                 area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
#             else:
#                 area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
#     elif row["Recommend System 2"]in['Shelf Rack']:
#         wh_length=100
#         c_height=0.5
#         c_width=0.3
#         c_length=0.4
#         aisle=3
#         level=4
#         s_depth=1.7
#         bay=1.28
#         num1=bay//c_length
#         num2=s_depth//c_width
#         sum_1=num1*num2*4
#         bay_line=(wh_length-0.3)//bay
#         no_bay=int(row["Bin Quantity"]//sum_1+1)
#         line=int(no_bay//bay_line+1)
#         if row["Bin Quantity"] <sum_1:
#             area=math.ceil(bay*s_depth)
#         elif row["Bin Quantity"] < bay_line*sum_1:
#             area=math.ceil(no_bay*bay*s_depth)
#         else:
#             area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
#     else:
#         area=0
#     return area
# dfx['Area'] = dfx.apply(lambda row: int(requireArea(row)) , axis=1)
# dfx3['Area (sqm)'] = dfx3.apply(lambda row: int(requireArea2(row)) , axis=1)

ta=result_p_CO.sort_values(by='Quantity', ascending=False)
t2=ta.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]] 
t2=t2.rename(columns={"Quantity":"Pallet Quantity"})
t2=t2.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
t2['Recommend System 1']=t2.idxmax(axis=1)
t2=t2.reset_index()
# print(t2)
t2=t2.iloc[:,[0,1,2,3,4,5,15]] 
# t2['Area (sqm)'] = t2.apply(lambda row: int(requireArea(row)) , axis=1)


tb=result_b_AC.sort_values(by='Quantity', ascending=False)
# t3=tb.iloc[:,[2,3,4,5]]
t3=tb.iloc[:,[2,3,4,5,6,7,8,9,10,11,12,13]] 
# print(t3)
t3=t3.rename(columns={"Quantity":"Bin Quantity"}) 
t3=t3.set_index(["ProductType","Bin Quantity","ProductRange","LOS%","OUT%","PAL%"])
t3['Recommend System 1']=t3.idxmax(axis=1)
t3=t3.reset_index()
t3=t3.iloc[:,[0,1,3,4,5,12]] 

tc=result_b_CO.sort_values(by='Quantity', ascending=False)
t4=tc.iloc[:,[2,3,4,5,6,7,8,9,10,11,12,13]]
t4=t4.rename(columns={"Quantity":"Bin Quantity"}) 
t4=t4.set_index(["ProductType","Bin Quantity","ProductRange","LOS%","OUT%","PAL%"])
t4['Recommend System 1']=t4.idxmax(axis=1)
t4=t4.reset_index()
t4=t4.iloc[:,[0,1,3,4,5,12]] 
# t4['Area (sqm)'] = t4.apply(lambda row: int(requireArea(row)) , axis=1)

tx=result_b_FZ.sort_values(by='Quantity', ascending=False)
t5=tx.iloc[:,[2,3,4,5,6,7,8,9,10,11,12,13]]
t5=t5.rename(columns={"Quantity":"Bin Quantity"}) 
t5=t5.set_index(["ProductType","Bin Quantity","ProductRange","LOS%","OUT%","PAL%"])
t5['Recommend System 1']=t5.idxmax(axis=1)
t5=t5.reset_index()
t5=t5.iloc[:,[0,1,3,4,5,12]] 
# t5['Area (sqm)'] = t5.apply(lambda row: int(requireArea(row)) , axis=1)



df7 = pd.read_csv (r'D:\OE\2810_June_Complete1.csv')
df7.columns = df7.columns.str.replace(' ', '')
df7 = df7.rename(columns={"StorageCondition":"WarehouseStorageCondition"})
df7 = df7.drop(df7[(df7.WarehouseStorageCondition==0)].index)
df7 = df7.drop(df7[(df7.Quantity==0)].index)
out_pr=df7.groupby(['WarehouseStorageCondition','MaterialGroup'])[['ProductNumber']].nunique().reset_index()
out_pr=out_pr.rename(columns={"MaterialGroup":"ProductType"})
out_pr=out_pr.rename(columns={"ProductNumber":"ProductRange"})
out_pr.head(10)
df7['PAL'] = df7.apply(lambda x: int(x[16] / x[17]) , axis=1)
df7['CAR'] = df7.apply(lambda x: int(x[16] / x[18]) , axis=1)
#  x if (x < 30 or x > 60) else 0
df7['PAL_QTY'] = df7.apply(lambda x: x[16] // x[19] , axis=1)
df7['LOS_QTY'] = df7.apply(lambda x: x[16] % x[20], axis=1)
# # # OUT_QTY: ([QTY]-[LOS_QTY]-([PAL_QTY]*[PAL]))/[CAR]
# # df7 = df7.fillna(0)
df7['OUT_QTY'] = df7.apply(lambda x: (x[16]-x[22]-(x[21])*x[19])/x[20], axis=1)
df7.loc[df7['LOS_QTY'] > 0, 'Los_FREQ'] = 1
df7.loc[df7['PAL_QTY'] > 0, 'PAL_FREQ'] = 1
df7.loc[df7['OUT_QTY'] > 0, 'OUT_FREQ'] = 1
df7 = df7.fillna(0)
table = df7.groupby(["WarehouseStorageCondition","MaterialGroup"]).apply(lambda s: pd.Series({ 
    "LosSum": s["Los_FREQ"].sum(), 
    "OutSum": s["OUT_FREQ"].sum(), 
    "PalSum": s["PAL_FREQ"].sum(), 
}))
# print(table)
table['TotalFreq'] =table.apply(lambda x: x[1] + x[0] + x[2], axis=1)
table['LOS%'] =table.apply(lambda x: x[0]/x[3]*100, axis=1).round(decimals=0)
table['OUT%'] =table.apply(lambda x: x[1]/x[3]*100, axis=1).round(decimals=0)
table['PAL%'] =table.apply(lambda x: x[2]/x[3]*100, axis=1).round(decimals=0)
pickdata=table.reset_index()
pickdata = pickdata.rename(columns={"MaterialGroup":"ProductType"})
pickdata=pickdata.drop(pickdata[(pickdata.WarehouseStorageCondition==0)].index)
pickdata.head()
pick2=pickdata[['WarehouseStorageCondition','ProductType','LOS%','OUT%','PAL%']]
dfp=pd.merge(pick2,out_pr,how="inner")
dfp=dfp.iloc[:,[0,1,2,3,4]] 
# print(dfp)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4("OE Design Tool", style={'text-align': 'center','font_size': '26px'}),
    # html.Div([html.H4("Space Requirement", style={'text-align': 'center','font_size': '26px'}),]),
    # html.H5("AC"),
     html.Div(children=[
         html.Div(children=[
            html.H6('Input Space Area (sqm) AC',style={'text-align': 'left'}),
            dcc.Input(
                id='ACspace',
                placeholder='Input Space Area (sqm)',
                type='number',
                value='10000',
            ),
            ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}),
         html.Div(children=[
            html.H6('Input warehouse height (m) AC',style={'text-align': 'left','font_size': '8px'}),
            dcc.Input(
                id='ACheight',
                placeholder='Input warehouse height (m)',
                type='number',

                value='12',
            ),
            ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}),

        html.Div(children=[
            html.H6('Input Space Area (sqm) NAC',style={'text-align': 'left','font_size': '8px'}),
            dcc.Input(
                id='NACspace',
                placeholder='Input Space Area (sqm)',
                type='number',
                value='10000',
            ),
        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}),
        html.Div(children=[
            html.H6('Input warehouse height (m) NAC',style={'text-align': 'left','font_size': '8px'}),
            dcc.Input(
                id='NACheight',
                placeholder='Input warehouse height (m)',
                type='number',
                value='12',
            ),

        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}),
    ]), 
    html.Div(children=[
        #  html.H5("CO"),
        html.Div(children=[
            html.H6('Input Space Area (sqm) CO'),
            dcc.Input(
                id='COspace',
                placeholder='Input Space Area (sqm)',
                type='number',
                value='1000',
            ),
         ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}),
         html.Div(children=[
             html.H6('Input warehouse height (m) CO'),
            dcc.Input(
                id='COheight',
                placeholder='Input warehouse height (m)',
                type='number',
                value='3',
            ),
         ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}),
            
        html.Div(children=[
        #  html.H5("FZ"),
            html.H6('Input Space Area (sqm) FZ'),
            dcc.Input(
                id='FZspace',
                placeholder='Input Space Area (sqm)',
                type='number',
                value='300',
            ),
        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}),
        html.Div(children=[
            html.H6('Input warehouse height (m) FZ'),
            dcc.Input(
                id='FZheight',
                placeholder='Input warehouse height (m)',
                type='number',
                value='3',
            ),
            
        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'5vw'}), 
            
    ]), 

    html.Div(children=[
        html.Div(children=[
            html.H5('Country'),
            dcc.Dropdown(
            id="selected_country",
            options = [{'label': 'tw', 'value': 'Taiwan'},
                       {'label': 'sg', 'value': 'Singapore'},
                       ],

            value = 'Taiwan',
            multi=False,
            style={'width':"10 px"},
            # style={'width': "30%"}
            ),
        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'3vw','width':'10vw'}),
        html.Div(children=[
            html.H5('Warehouse Name'),
            dcc.Dropdown(
            id="selected_whname",
            options = [{'label': 'DC1', 'value': 'Dayuan DC1'},
                       {'label': 'DC2', 'value': 'Dayuan DC2'},
                       ],
            value = 'Dayuan DC1',
            multi=False,
            # style={'width': "30%"}
            ),
        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'3vw','width':'15vw'}),
        html.Div(children=[
            html.H5('Plan Code'),
            dcc.Dropdown(
            id="selected_plancode",
            options = [{'label': '2810', 'value': '2810'},
                       {'label': '2811', 'value': '2811'},
                       ],
            value = '2810',
            multi=False,
            # style={'width': "30%"}
            ),
        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'3vw','width':'15vw'}), 
        html.Div(children=[
            html.H5('Duration of Analysis (months):'),
            dcc.Dropdown(
                 id="slct_month",
                 options=[
                            {"label": i, "value": i}
                            for i in range(1,13)
                        ],
                value = '1',
                multi=False,
                style={'width': "100%"}),
        ],style={'display': 'inline-block', 'vertical-align': 'top','margin-right':'3vw','width':'20vw'}),
        html.Div(children=[
            html.H5('Projected Growth Years:'),
            dcc.Dropdown(
                 id="slct_year",
                 options=[
                            {"label": i, "value": i}
                            for i in range(1,11)
                        ],
                value = '1',
                multi=False,
                ),
   
        ],style={'display': 'inline-block', 'vertical-align': 'top','width':'15vw'}),

    ]),
    html.H4("Order Profile", style={'text-align': 'center','font_size': '26px'}),
    # html.Div([
    #     html.Div([
    #         dcc.Dropdown(id='piedropdown',
    #         options=[
    #                  {'label': 'SKU', 'value': 'SKU'},
    #                  {'label': 'HITS', 'value': 'HITS'},
    #                  {'label': 'SOH_QTY', 'value': 'SOH_QTY'}
    #         ],
    #         value='cases',
    #         multi=False,
    #         clearable=False
    #     ),
    #         dcc.Graph(id='piechart', figure={})
    #     ]),
    # ]),
    html.Div([
        
        html.Div([
            
            html.H5('Product Type'),
            dcc.Dropdown(id="slct_impact",
                 options=[{"label": x, "value":x} for x in all_pt],
                 value="Phrama Ethical",
                 multi=False,
                 style={'width': "80%"}
                 ),
            
            dcc.Graph(id='graph', figure={}),
        ]),

        html.Div([
            dcc.Graph(id='graph2', figure={})
        ]),

    ],style={'columnCount':2 }),
    
    # html.Div([
    #     html.Div([
    #     dcc.Graph(id='graph3', figure={}),
    #     ]),

    # ]),
    html.Br(),
    html.Br(),
    html.Div([
        html.H3("System Recommendation Warhouse Condition: Aircon, StorageUOM: Pallet", style={'text-align': 'center'}),
        html.Div([
            html.Div(id="tableAC",style={'display': 'inline-block'}),
            # dash_table.DataTable(
            # style_data={
            #     'whiteSpace': 'normal',
            #     'height': 'auto',
            #     'lineHeight': '15px'
            # },
            # id='table',
            # columns=[{"name": i, "id": i} for i in dfx.columns],
            # data=dfx.to_dict('records'),
            # editable=False,
            # page_action="native",
            # page_current= 0,
            # page_size= 6,
            # style_cell_conditional=[
            #     {'if': {'column_id': 'WarehouseStorageConditon'},
            #      'width': '40%', 'textAlign': 'left'},
            #     {'if': {'column_id': 'Selective Pallet Racking (SPR)'},
            #      'width': '10%', 'textAlign': 'left'},
            # ],
            
            # ),
            # html.Div([
            #     html.H5("SPR Photo"),
            #     html.Img(id= 'SPR', src='https://portalimages.blob.core.windows.net/thumbnails/images/p52olmr5_1-375x300.jpg')
            # ],style={'display': 'inline-block'}),
        ],style={'display': 'inline-block'}),
    #    html.Div([
            
    #         # dash_table.DataTable(
    #         # style_data={
    #         #     'whiteSpace': 'normal',
    #         #     'height': 'auto',
    #         #     'lineHeight': '15px'
    #         # },
    #         # id='tabler',
    #         # columns=[{"name": i, "id": i} for i in dfx3.columns],
    #         # data=dfx3.to_dict('records'),
    #         # editable=False,
    #         # page_action="native",
    #         # page_current= 0,
    #         # page_size= 6,
    #         # style_cell_conditional=[
    #         #     {'if': {'column_id': 'WarehouseStorageConditon'},
    #         #      'width': '40%', 'textAlign': 'left'},
    #         #     {'if': {'column_id': 'Selective Pallet Racking (SPR)'},
    #         #      'width': '10%', 'textAlign': 'left'},
    #         # ],
            
    #     ),
        
        # html.Div([
        #         html.H5("VNA Photo"),
        #         html.Img(id= 'VNA', src='https://tse1.mm.bing.net/th?id=OIP.lQnuf870Hq-fac2FZpWaMAHaEo&pid=Api&P=0&w=278&h=174')
        #     ],style={'display': 'inline-block'}),
        # # html.Div([
        # #         html.H5("Ground Storage Photo"),
        # #         html.Img(id= 'GRS', src='D:\OE\photo\VNA.png')
        # #     ],style={'display': 'inline-block'}),
        
        # ],style={'display': 'inline-block'}),    
        
    ]),

    # html.Div([
            
    #         # dash_table.DataTable(
    #         # style_data={
    #         #     'whiteSpace': 'normal',
    #         #     'height': 'auto',
    #         #     'lineHeight': '15px'
    #         # },
    #         # id='tabler3',
    #         # columns=[{"name": i, "id": i} for i in dfx5.columns],
    #         # data=dfx5.to_dict('records'),
    #         # editable=False,
    #         # page_action="native",
    #         # page_current= 0,
    #         # page_size= 6,
    #         # style_cell_conditional=[
    #         #     {'if': {'column_id': 'WarehouseStorageConditon'},
    #         #      'width': '40%', 'textAlign': 'left'},
    #         #     {'if': {'column_id': 'Selective Pallet Racking (SPR)'},
    #         #      'width': '10%', 'textAlign': 'left'},
    #         # ],
            
    #         # ),
    #         # html.Div([
    #         #     html.H5("ASRS Photo"),
    #         #     html.Img(id= 'ASRS', src='https://3.imimg.com/data3/YL/IR/MY-2255203/asrs-automated-storage-and-retrieval-system-500x500.jpg')
    #         # ],style={'display': 'inline-block'}),
    #         # html.Div([
    #         #     html.H5("Shuttle Storage System Photo"),
    #         #     html.Img(id= 'Shuttle Storage System', src='https://tse2.mm.bing.net/th?id=OIP.H-6WJBU3bKrl010TQ54N_QHaHD&pid=Api&P=0&w=172&h=165')
    #         # ],style={'display': 'inline-block'}),
    #     ],style={'display': 'inline-block'}),

     html.Div([
        html.H3("System Recommendation Total Socre:7 Warhouse Condition: Cold Room, StorageUOM: Pallet", style={'text-align': 'center'}),
        html.Div(id="tableCOP",style={'display': 'inline-block'}),
        # dash_table.DataTable(
        #     style_data={
        #         'whiteSpace': 'normal',
        #         'height': 'auto',
        #         'lineHeight': '15px'
        #     },
        #     id='table2',
        #     columns=[{"name": i, "id": i} for i in t2.columns],
        #     data=t2.to_dict('records'),
        #     editable=False,
        #     page_action="native",
        #     page_current= 0,
        #     page_size= 6,
        #     style_cell_conditional=[
        #         {'if': {'column_id': 'WarehouseStorageConditon'},
        #          'width': '40%', 'textAlign': 'left'},
        #         {'if': {'column_id': 'Selective Pallet Racking (SPR)'},
        #          'width': '30%', 'textAlign': 'left'},
        #     ],
        # )
        
    ]),
    html.Div([
        html.H3("System Recommendation Warhouse Condition: Aircon, StorageUOM: Bin", style={'text-align': 'center'}),
        html.Div(id="tableACB",style={'display': 'inline-block'}),
        # dash_table.DataTable(
        #     style_data={
        #         'whiteSpace': 'normal',
        #         'height': 'auto',
        #         'lineHeight': '15px'
        #     },
        #     id='table3',
        #     columns=[{"name": i, "id": i} for i in t3.columns],
        #     data=t3.to_dict('records'),
        #     editable=False,
        #     page_action="native",
        #     page_current= 0,
        #     page_size= 6,
        #     style_cell_conditional=[
        #         {'if': {'column_id': 'WarehouseStorageConditon'},
        #          'width': '40%', 'textAlign': 'left'},
        #         {'if': {'column_id': 'Selective Pallet Racking (SPR)'},
        #          'width': '30%', 'textAlign': 'left'},
        #     ],
        # )
        
    ]),
    html.Div([
        html.H3("System Recommendation Total Socre:5 Warhouse Condition: Cold Room, StorageUOM: Bin", style={'text-align': 'center'}),
        html.Div(id="tableCOB",style={'display': 'inline-block'}),
        # dash_table.DataTable(
        #     style_data={
        #         'whiteSpace': 'normal',
        #         'height': 'auto',
        #         'lineHeight': '15px'
        #     },
        #     id='table4',
        #     columns=[{"name": i, "id": i} for i in t4.columns],
        #     data=t4.to_dict('records'),
        #     editable=False,
        #     page_action="native",
        #     page_current= 0,
        #     page_size= 6,
        #     style_cell_conditional=[
        #         {'if': {'column_id': 'WarehouseStorageConditon'},
        #          'width': '40%', 'textAlign': 'left'},
        #         {'if': {'column_id': 'Selective Pallet Racking (SPR)'},
        #          'width': '20%', 'textAlign': 'left'},
        #     ],
        # )
        
    ]),
    html.Div([
        html.H3("System Recommendation Total Socre:5 Warhouse Condition: Freezer, StorageUOM: Bin", style={'text-align': 'center'}),
        html.Div(id="tableFZB",style={'display': 'inline-block'}),
        # dash_table.DataTable(
        #     style_data={
        #         'whiteSpace': 'normal',
        #         'height': 'auto',
        #         'lineHeight': '15px'
        #     },
        #     id='table5',
        #     columns=[{"name": i, "id": i} for i in t5.columns],
        #     data=t5.to_dict('records'),
        #     editable=False,
        #     page_action="native",
        #     page_current= 0,
        #     page_size= 6,
        #     style_cell_conditional=[
        #         {'if': {'column_id': 'WarehouseStorageConditon'},
        #          'width': '40%', 'textAlign': 'left'},
        #         {'if': {'column_id': 'Selective Pallet Racking (SPR)'},
        #          'width': '30%', 'textAlign': 'left'},
        #     ],
        # )
        
    ]),
     

])

@app.callback(
    [ 
     Output(component_id='graph', component_property='figure'),
     Output(component_id='graph2', component_property='figure'),
    ],
    [    
    Input(component_id='slct_impact', component_property='value'),
     Input(component_id='slct_year', component_property='value')]
)

def update_graph(option_slctd,option_slcted2):
    
    # pie_chart=px.pie(
    #     data_frame=dfA,
    #     names='ABC_CLASS',
    #     value=dfA['piedropval'],
    #     labels={'ABC_CLASS':'ABC_CLASS'}
    # )
    # print(option_slctd)
    # print(type(option_slctd))
    # print(option_slcted2)
    # print(type(option_slcted2))
    # container = "The product type user choose is : {}".format(option_slctd)

    dff = bm.copy()
    dff = dff[dff["ProductType"] == option_slctd]
    # dff = dff[(dff["WarehouseStorageCondition"] == "AC")]

    fig = px.bar(
        data_frame=dff,
        x='Batch',
        y='%',
        hover_data=['Batch', '%'],
        labels={'Batch': 'Number of Pallet Per Batch'},
        # template='plotly_dark'
    )
    x=int(option_slcted2)+4
    # print(x)
    dff2= spt.copy()
    dff2=dff2[(dff2["StorageUOM"] == "Pallet") &(dff2['WarehouseStorageCondition']=='AC')]
    dff2=dff2.iloc[:,[2,3,4,5,6,7,8,9,10,11,12]]
    years=list(dff2.ProductType.unique())
    # print(years)
    # dff2=dff2.transpose()
    # print(dff2)
    
    
    trace1 = go.Bar(x=dff2['Pallet Quantity'], y=years, name='2021')
    trace2 = go.Bar(x=dff2['2022'], y=[years,dff2['2022']], name='2022')
    trace3 = go.Bar(x=dff2['2023'], y=years, name='2023')
    trace4 = go.Bar(x=dff2['2024'], y=years, name='2024')
    trace5 = go.Bar(x=dff2['2025'], y=years, name='2025')
    trace6 = go.Bar(x=dff2['2026'], y=years, name='2026')
    trace7 = go.Bar(x=dff2['2027'], y=years, name='2027')
    trace8 = go.Bar(x=dff2['2028'], y=years, name='2028')
    trace9 = go.Bar(x=dff2['2029'], y=years, name='2029')
    trace10 = go.Bar(x=dff2['2030'], y=years, name='2030')
    # print(dff2)
    data = [trace1, trace2, trace3, trace4, trace5,trace6,trace7,trace8,trace9]
    layout = go.Layout(
    barmode='stack',
    xaxis=dict(tickvals=years)
)

    fig2= go.Figure(data=data, layout=layout)
    #     data_frame=dff2,
    #     x='ProductType',
    #     y='Pallet Quantity',
    #     hover_data=['ProductType', 'Pallet Quantity'],
    #     labels={'ProductType': 'Product Type'},
    #     # template='plotly_dark'
    # )
    return  fig, fig2

@app.callback(
    dash.dependencies.Output("tableAC","children"),
    [dash.dependencies.Input("ACheight","value")]
)
def calAreaAC(acheight):
    wh_height=acheight
    # print(wh_height)
    def requireAreaAC(row):
        if row["Recommend System 1"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
            # wh_height=12
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=4
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
        elif row["Recommend System 1"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=2.8
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
        elif row["Recommend System 1"]in['Double Deep Racking (DDR)']:
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=2.8
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
        elif row["Recommend System 1"]in['Shuttle Storage System']:
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=1.5
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
    
        else:
            area=0
        return area
    dfx['Area(sqm)'] = dfx.apply(lambda row: int(requireAreaAC(row)) , axis=1)
    total = dfx['Area(sqm)'].sum()
    # dfx=dfx.iloc[:,[0,1,2,3,4,5,6,8]
    # print(dfx)
    return html.Div([
        dash_table.DataTable(
            data=dfx.to_dict('records'),
            columns=[{"name": i, "id": i} for i in dfx.columns],
            
            editable=False,
        ),
        html.H5("Total Area need is"+str(total)+"square meters")
        
    ],style={'display': 'inline-block'})

@app.callback(
    dash.dependencies.Output("tableCOP","children"),
    [dash.dependencies.Input("COheight","value")]
)
def calAreaCOP(coheight):
    wh_height=coheight
    # print(wh_height)
    def requireAreaCO(row):
        if row["Recommend System 1"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
            # wh_height=12
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=4
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
        elif row["Recommend System 1"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=2.8
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
        elif row["Recommend System 1"]in['Double Deep Racking (DDR)']:
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=2.8
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
        elif row["Recommend System 1"]in['Shuttle Storage System']:
            wh_length=100
            p_height=1.8
            p_width=0.8
            p_length=1.2
            aisle=1.5
            level=wh_height //(p_height+0.4)
            onebay=level*3
            num=(wh_length-0.3)//2.8
            sum_1=num*level*3
            if row["Pallet Quantity"] <= onebay:
                area=2.7*0.8
            elif row["Pallet Quantity"]<= sum_1:
                num2=int(row["Pallet Quantity"]/onebay)
                area=num2*2.7*0.8
            elif row["Pallet Quantity"]> sum_1: 
                no_bay=row["Pallet Quantity"]//sum_1
                lef=row["Pallet Quantity"]%sum_1
                if no_bay<2:
                    area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                else:
                    area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
        else:
            area=0
        return area
    t2['Area(sqm)'] = t2.apply(lambda row: int(requireAreaCO(row)) , axis=1)
    total = t2['Area(sqm)'].sum()
    # dfx=dfx.iloc[:,[0,1,2,3,4,5,6,8]
    # print(t2)
    return html.Div([
        dash_table.DataTable(
            data=t2.to_dict('records'),
            columns=[{"name": i, "id": i} for i in t2.columns],
            
            editable=False,
        ),
        html.H5("Total Area need is "+str(total)+" square meters")
        
    ],style={'display': 'inline-block'})

@app.callback(
    dash.dependencies.Output("tableACB","children"),
    [dash.dependencies.Input("ACheight","value")]
)
def calAreaACB(acheight):
    wh_height=acheight

    def requireAreaACB(row):
        if row["Recommend System 1"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=3
            level=4
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*4
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                area=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        elif row["Recommend System 1"]in['High Bay Shelf Rack']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=2.8
            level=wh_height//c_height
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*level
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                    rea=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        elif row["Recommend System 1"]in['Vertical Carousel Storage']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=2.5
            level=wh_height//c_height
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*level
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                area=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        else:
            area=0
        return area
    t3['Area(sqm)'] = t3.apply(lambda row: int(requireAreaACB(row)) , axis=1)
    total = t3['Area(sqm)'].sum()
    # dfx=dfx.iloc[:,[0,1,2,3,4,5,6,8]
    # print(t3)
    return html.Div([
        dash_table.DataTable(
            data=t3.to_dict('records'),
            columns=[{"name": i, "id": i} for i in t3.columns],
            
            editable=False,
        ),
        html.H5("Total Area need is "+str(total)+" square meters")
        
    ],style={'display': 'inline-block'})

@app.callback(
    dash.dependencies.Output("tableCOB","children"),
    [dash.dependencies.Input("COheight","value")]
)
def calAreaCOB(coheight):
    wh_height=coheight

    def requireAreaCOB(row):
        if row["Recommend System 1"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=3
            level=4
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*4
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                area=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        elif row["Recommend System 1"]in['High Bay Shelf Rack']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=2.8
            level=wh_height//c_height
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*level
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                    rea=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        elif row["Recommend System 1"]in['Vertical Carousel Storage']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=2.5
            level=wh_height//c_height
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*level
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                area=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        else:
            area=0
        return area
    t4['Area(sqm)'] = t4.apply(lambda row: int(requireAreaCOB(row)) , axis=1)
    total = t4['Area(sqm)'].sum()
    # dfx=dfx.iloc[:,[0,1,2,3,4,5,6,8]
    # print(t4)
    return html.Div([
        dash_table.DataTable(
            data=t4.to_dict('records'),
            columns=[{"name": i, "id": i} for i in t4.columns],
            
            editable=False,
        ),
        html.H5("Total Area need is "+str(total)+" square meters")
        
    ],style={'display': 'inline-block'})

@app.callback(
    dash.dependencies.Output("tableFZB","children"),
    [dash.dependencies.Input("FZheight","value")]
)
def calAreaFZB(fzheight):
    wh_height=fzheight

    def requireAreaFZB(row):
        if row["Recommend System 1"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=3
            level=4
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*4
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                area=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        elif row["Recommend System 1"]in['High Bay Shelf Rack']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=2.8
            level=wh_height//c_height
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*level
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                    rea=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        elif row["Recommend System 1"]in['Vertical Carousel Storage']:
            wh_length=100
            c_height=0.5
            c_width=0.3
            c_length=0.4
            aisle=2.5
            level=wh_height//c_height
            s_depth=1.7
            bay=1.28
            num1=bay//c_length
            num2=s_depth//c_width
            sum_1=num1*num2*level
            bay_line=(wh_length-0.3)//bay
            no_bay=int(row["Bin Quantity"]//sum_1+1)
            line=int(no_bay//bay_line+1)
            if row["Bin Quantity"] <sum_1:
                area=math.ceil(bay*s_depth)
            elif row["Bin Quantity"] < bay_line*sum_1:
                area=math.ceil(no_bay*bay*s_depth)
            else:
                area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
        else:
            area=0
        return area
    t5['Area(sqm)'] = t5.apply(lambda row: int(requireAreaFZB(row)) , axis=1)
    total = t5['Area(sqm)'].sum()
    # dfx=dfx.iloc[:,[0,1,2,3,4,5,6,8]
    # print(t5)
    return html.Div([
        dash_table.DataTable(
            data=t5.to_dict('records'),
            columns=[{"name": i, "id": i} for i in t5.columns],
            
            editable=False,
        ),
        html.H5("Total Area need is "+str(total)+" square meters")
        
    ],style={'display': 'inline-block'})

app.run_server(debug=True)