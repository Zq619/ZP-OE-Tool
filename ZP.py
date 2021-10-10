import re
from tkinter import Tk
from tkinter.constants import NONE     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import webbrowser
from threading import Timer
import dash
from dash_html_components.Br import Br
from dash_html_components.H2 import H2
import dash_table
import math
from numpy import empty
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import sys
# Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
# filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
filename='INT_Sample_OE.xlsx'
if "xlsx" in filename :
    #dfA no nned modify, just show the result 
    area=0
    dfArea=pd.DataFrame(columns=['WarehouseStorageCondition','StorageUOM','Total Area(sqm)'])
    dfArea2=pd.DataFrame(columns=['WarehouseStorageCondition','StorageUOM','Total Area(sqm)'])
    dfArea3=pd.DataFrame(columns=['WarehouseStorageCondition','StorageUOM','Total Area(sqm)'])
    dfstock= pd.read_excel (filename,'Stocks on hand')#stock data
    df_outbound = pd.read_excel (filename,'Outbound Data')#Outbound data
    df_inbound=pd.read_excel (filename,'Inbound Data')#Outbound data
    #calculate ABC
    abc_1=df_outbound.groupby(['StorageCondition','DOCNO','ProductNumber'])[['Quantity']].sum().reset_index()
    abc_2=abc_1.groupby(['StorageCondition','ProductNumber','Quantity'])[['DOCNO']].nunique().reset_index()
    abc_2_1=abc_2.groupby(['StorageCondition','ProductNumber'])[['Quantity','DOCNO']].sum().reset_index()
    abc_ac=abc_2_1[abc_2_1['StorageCondition'].str.contains('AC')]
    abc_ac['HIT%'] = (abc_ac['DOCNO'] / abc_ac['DOCNO'].sum()) * 100
    abc_ac = abc_ac.sort_values('HIT%', ascending=False)
    abc_ac['cumulative_%']=abc_ac['HIT%'].cumsum(axis = 0) 
    abc_co=abc_2_1[abc_2_1['StorageCondition'].str.contains('CO')]
    abc_co['HIT%'] = (abc_co['DOCNO'] / abc_co['DOCNO'].sum()) * 100
    abc_co = abc_co.sort_values('HIT%', ascending=False)
    abc_co['cumulative_%']=abc_co['HIT%'].cumsum(axis = 0)
    abc_fz=abc_2_1[abc_2_1['StorageCondition'].str.contains('FZ')]
    abc_fz['HIT%'] = (abc_fz['DOCNO'] / abc_fz['DOCNO'].sum()) * 100
    abc_fz = abc_fz.sort_values('HIT%', ascending=False)
    abc_fz['cumulative_%']=abc_fz['HIT%'].cumsum(axis = 0)
    def ABC_Class(row):
        if row['cumulative_%']<=40:
            value = "AA"
        elif row['cumulative_%']<=80:
            value = "A"
        elif row['cumulative_%']<=95:
            value = "B"
        elif row['cumulative_%']<=97.5:
            value = "C"    
        else:
            value="CC"
        return value
    abc_ac['ABC_CLASS'] = abc_ac.apply(lambda row: ABC_Class(row), axis=1)
    abc_co['ABC_CLASS'] = abc_co.apply(lambda row: ABC_Class(row), axis=1)
    abc_fz['ABC_CLASS'] = abc_fz.apply(lambda row: ABC_Class(row), axis=1)
    abc_3=pd.merge(abc_ac,abc_co,how='outer')
    dfABC=pd.merge(abc_3,abc_fz,how='outer')
    abc_3=pd.merge(abc_ac,abc_co,how='outer')
    dfABC=pd.merge(abc_3,abc_fz,how='outer')
    #calculate product range output, output dataframe: pr
    datafilter = dfstock.loc[dfstock['StorageBin'].str.len() == 12].reset_index()
    datafilter = datafilter.rename(columns={"StorageCondition":"WarehouseStorageCondition"})
    datafilter = datafilter.rename(columns={"StorageBin":"BinType"})
    datafilter = datafilter.rename(columns={"MaterialGroup":"ProductType"})
    pr=datafilter.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['Material']].nunique().reset_index()

    #calculate number of pallet per batch and percentage, output dataframe: bm

    selection=datafilter[datafilter['StorageUOM'].str.contains('Pallet')]
    selection1=selection.groupby(['WarehouseStorageCondition','StorageUOM','ProductType','Pallet'])[['Batch']].count().reset_index()
    selection1.set_index(['WarehouseStorageCondition','ProductType'],inplace=True)
    selection1['%'] = (100*selection1['Batch']/selection1['Batch'].groupby(level ='ProductType').sum()).round(2)
    b1=selection1.reset_index()
    bn=b1.groupby(['WarehouseStorageCondition','StorageUOM','ProductType','Batch'])[['Pallet']].count().reset_index()
    bn.set_index(['WarehouseStorageCondition','ProductType'],inplace=True)
    bn['%'] = (100*bn['Pallet']/bn['Pallet'].groupby(level ='ProductType').sum()).round(2)
    bx=bn.reset_index()
    bm=bx.drop(bx[(bx.Batch==0)].index)
    projectlist=bm["ProductType"].drop_duplicates(keep='first', inplace=False).astype("string")
    conditionlist=bm["WarehouseStorageCondition"].drop_duplicates(keep='first', inplace=False).astype("string")


    #select the number of the batch =1,2,3,4 and seperate into 4 tables as user only want show result of 1,2,3,4
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
    #join the selected result into one table , output dataframe bm3
    bm1=pd.merge(b3,b4,how='outer')
    bm2=pd.merge(bm1,b5,how='outer')
    bm3=pd.merge(bm2,b6,how='outer')

    # calculate the Pallet quantity and Bin quantity based on the raw SAP data by count the pallet/bin column
    #and seperate into 6 tables based on the wh condition and storage UOM
    # output:SPT dataframe is the combine of those 6 tables as a overall result.
    #spt:4 columns : WarehouseStorageCondition,StorageUOM,ProductType and Quantity(refer to the UOM Quantity)

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

    # this function is based on the different growth rate to calculate the next 10 year storage growth
    #output dataframe below is spt

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

    # table of los out pallet percentage , output dataframe as orderprofile
    df_outbound.columns = df_outbound.columns.str.replace(' ', '')
    df_outbound = df_outbound.rename(columns={"StorageCondition":"WarehouseStorageCondition"})
    df_outbound = df_outbound.drop(df_outbound[(df_outbound.WarehouseStorageCondition==0)].index)
    df_outbound = df_outbound.drop(df_outbound[(df_outbound.Quantity==0)].index)
    df_outbound['PAL'] = df_outbound.apply(lambda x: int(x[16] / x[17]) , axis=1)
    df_outbound['CAR'] = df_outbound.apply(lambda x: int(x[16] / x[18]) , axis=1)
    df_outbound['PAL_QTY'] = df_outbound.apply(lambda x: x[16] // x[19] , axis=1)
    df_outbound['LOS_QTY'] = df_outbound.apply(lambda x: x[16] % x[20], axis=1)
    df_outbound['OUT_QTY'] = df_outbound.apply(lambda x: (x[16]-x[22]-(x[21])*x[19])/x[20], axis=1)
    df_outbound.loc[df_outbound['LOS_QTY'] > 0, 'Los_FREQ'] = 1
    df_outbound.loc[df_outbound['PAL_QTY'] > 0, 'PAL_FREQ'] = 1
    df_outbound.loc[df_outbound['OUT_QTY'] > 0, 'OUT_FREQ'] = 1
    df_outbound = df_outbound.fillna(0)
    df_outbound = df_outbound.groupby(["WarehouseStorageCondition","MaterialGroup"]).apply(lambda s: pd.Series({ 
        "LosSum": s["Los_FREQ"].sum(), 
        "OutSum": s["OUT_FREQ"].sum(), 
        "PalSum": s["PAL_FREQ"].sum(), 
    }))
    df_outbound['TotalFreq'] =df_outbound.apply(lambda x: x[1] + x[0] + x[2], axis=1)
    df_outbound['LOS%'] =df_outbound.apply(lambda x: x[0]/x[3]*100, axis=1).round(decimals=0)
    df_outbound['OUT%'] =df_outbound.apply(lambda x: x[1]/x[3]*100, axis=1).round(decimals=0)
    df_outbound['PAL%'] =df_outbound.apply(lambda x: x[2]/x[3]*100, axis=1).round(decimals=0)
    df_outbound=df_outbound.reset_index()
    df_outbound = df_outbound.rename(columns={"MaterialGroup":"ProductType"})
    df_outbound=df_outbound.drop(df_outbound[(df_outbound.WarehouseStorageCondition==0)].index)

    orderprofile=df_outbound[['WarehouseStorageCondition','ProductType','LOS%','OUT%','PAL%']]
    profileprojectlist=orderprofile["ProductType"].drop_duplicates(keep='first', inplace=False).astype("string")
    profileconditionlist=orderprofile["WarehouseStorageCondition"].drop_duplicates(keep='first', inplace=False).astype("string")
    #merge the different result table into one 
    #for pallet recommend, need to merge the pallet quantity,product ranage, no.of pallet per batch as input data
    #for carton reommendation, need to mearge the orderprofile with the carton quantity
    merge=pd.merge(bm3,pr,how='inner')
    merge=merge.rename(columns={"Material":"ProductRange"})
    p_inner=pd.merge(m2,merge,how='inner')
    p_inner = p_inner.fillna(0)
    c_inner1=pd.merge(m4,pr,how='inner')
    c_inner=pd.merge(c_inner1,orderprofile,how="inner")
    c_inner = c_inner.fillna(0)
    c_inner=c_inner.rename(columns={"Material":"ProductRange"})


    # function sys1 to sys12  is for pallet recommendation score system
    #result dataframe as result_p
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
    result_p=p_inner.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]]  

    #from sys13 to sys18 is for bin recommendation score system 
    #result dataframe as result_b
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

    # seperate the table by different warehouse condition and storage UOM
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
    print(result_b_AC)
    #find the highest score in each table 
    #pallet AC
    t0=result_p_AC.sort_values(by='Quantity', ascending=False)
    t1=t0.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]] 
    t1=t1.set_index(["ProductType","Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
    #pallet CO
    t2=result_p_CO.sort_values(by='Quantity', ascending=False)
    t3=t2.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]] 
    t3=t3.set_index(["ProductType","Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
    #bin AC
    t4=result_b_AC.sort_values(by='Quantity', ascending=False)
    t5=t4.iloc[:,[2,3,4,5,6,7,8,9,10,11,12,13]] 
    t5=t5.set_index(["ProductType","Quantity","ProductRange","LOS%","OUT%","PAL%"])
    #bin CO
    t6=result_b_CO.sort_values(by='Quantity', ascending=False)
    t7=t6.iloc[:,[2,3,4,5,6,7,8,9,10,11,12,13]]  
    t7=t7.set_index(["ProductType","Quantity","ProductRange","LOS%","OUT%","PAL%"])
    #bin FZ
    t8=result_b_FZ.sort_values(by='Quantity', ascending=False)
    t9=t8.iloc[:,[2,3,4,5,6,7,8,9,10,11,12,13]]  
    t9=t9.set_index(["ProductType","Quantity","ProductRange","LOS%","OUT%","PAL%"])
    #funciton to find the highest 3 recommendations 
    def highest_3_recommendation(df):
        x=pd.DataFrame(df[df.columns[0:]]).T
        rslt = pd.DataFrame(np.zeros((0,3)), columns=['Recommend System 1','Recommend System 2','Recommend System 3'])
        for i in x.columns:
            df1row = pd.DataFrame(x.nlargest(3, i).index.tolist(), index=['Recommend System 1','Recommend System 2','Recommend System 3']).T
            rslt = pd.concat([rslt, df1row], axis=0,ignore_index=True)
        return rslt

    pallet_AC=highest_3_recommendation(t1)
    pallet_CO=highest_3_recommendation(t3)
    bin_AC=highest_3_recommendation(t5)
    bin_CO=highest_3_recommendation(t7)
    bin_FZ=highest_3_recommendation(t9)
    #Pallet AC 3 recommendation table
    p_AC_R=result_p_AC.join(pallet_AC)
    p_AC_R1=p_AC_R.iloc[:,[2,3,4,5,6,7,18]] 
    p_AC_R1=p_AC_R1.rename(columns={"Recommend System 1":"Recommend System"}) 
    p_AC_R2=p_AC_R.iloc[:,[2,3,4,5,6,7,19]] 
    p_AC_R2=p_AC_R2.rename(columns={"Recommend System 2":"Recommend System"}) 
    p_AC_R3=p_AC_R.iloc[:,[2,3,4,5,6,7,20]] 
    p_AC_R3=p_AC_R3.rename(columns={"Recommend System 3":"Recommend System"}) 
    #Pallet CO 3 recommendation table
    result_p_CO = result_p_CO.reset_index(drop=True)
    p_CO_R=result_p_CO.join(pallet_CO)
    p_CO_R1=p_CO_R.iloc[:,[2,3,4,5,6,7,18]] 
    p_CO_R2=p_CO_R.iloc[:,[2,3,4,5,6,7,19]] 
    p_CO_R3=p_CO_R.iloc[:,[2,3,4,5,6,7,20]] 
    p_CO_R1=p_CO_R1.rename(columns={"Recommend System 1":"Recommend System"}) 
    p_CO_R2=p_CO_R2.rename(columns={"Recommend System 2":"Recommend System"}) 
    p_CO_R3=p_CO_R3.rename(columns={"Recommend System 3":"Recommend System"}) 
    #Bin AC 3 recommendation table
    result_b_AC = result_b_AC.reset_index(drop=True)
    b_AC_R=result_b_AC.join(bin_AC)
    b_AC_R.head()
    b_AC_R1=b_AC_R.iloc[:,[2,3,5,6,7,14]] 
    b_AC_R2=b_AC_R.iloc[:,[2,3,5,6,7,15]] 
    b_AC_R3=b_AC_R.iloc[:,[2,3,5,6,7,16]] 
    b_AC_R1=b_AC_R1.rename(columns={"Recommend System 1":"Recommend System"}) 
    b_AC_R2=b_AC_R2.rename(columns={"Recommend System 2":"Recommend System"}) 
    b_AC_R3=b_AC_R3.rename(columns={"Recommend System 3":"Recommend System"}) 
    #Bin CO 3 recommendation table
    result_b_CO = result_b_CO.reset_index(drop=True)
    b_CO_R=result_b_CO.join(bin_CO)
    b_CO_R.head()
    b_CO_R1=b_CO_R.iloc[:,[2,3,5,6,7,14]] 
    b_CO_R2=b_CO_R.iloc[:,[2,3,5,6,7,15]] 
    b_CO_R3=b_CO_R.iloc[:,[2,3,5,6,7,16]] 
    b_CO_R1=b_CO_R1.rename(columns={"Recommend System 1":"Recommend System"}) 
    b_CO_R2=b_CO_R2.rename(columns={"Recommend System 2":"Recommend System"}) 
    b_CO_R3=b_CO_R3.rename(columns={"Recommend System 3":"Recommend System"}) 
    #Bin FZ 3 recommendation table
    result_b_FZ = result_b_FZ.reset_index(drop=True)
    b_FZ_R=result_b_FZ.join(bin_FZ)
    b_FZ_R.head()
    b_FZ_R1=b_FZ_R.iloc[:,[2,3,5,6,7,14]] 
    b_FZ_R2=b_FZ_R.iloc[:,[2,3,5,6,7,15]] 
    b_FZ_R3=b_FZ_R.iloc[:,[2,3,5,6,7,16]] 
    b_FZ_R1=b_FZ_R1.rename(columns={"Recommend System 1":"Recommend System"}) 
    b_FZ_R2=b_FZ_R2.rename(columns={"Recommend System 2":"Recommend System"}) 
    b_FZ_R3=b_FZ_R3.rename(columns={"Recommend System 3":"Recommend System"}) 
    #below are dash front end

    app = dash.Dash(__name__)
    tabs_styles = {
                                'font-family': 'Arial','height': '44px','display': 'flex','flex-direction': 'row',
                            }
    tab_style = {               'font-family': 'Arial',
                                'borderBottom': '1px solid #003948',
                                'padding': '6px',
                                'color':'white',
                                'fontWeight': 'bold',
                                'backgroundColor': '#005d62',
                            }

    tab_selected_style = {      'font-family': 'Arial',
                                'borderTop': '1px solid #003948',
                                'borderBottom': '1px solid #003948',
                                'backgroundColor': '#729748',
                                'color': 'white',
                                'padding': '6px'
                            }
    app.layout = html.Div([
        html.H1("OE Design Tool", style={'font-family': 'Arial','text-align': 'left','font_size': '26px','color':'#003948',}),       
        html.Div(children=[
        html.Div(children=[
            html.Div(id="Proloc",children=[
                html.Div(children=[
                                        html.H2('Project Location',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),
                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','background':'#005d62'}), 
                html.Div(children=[
                    html.H4('Country',style={'font-family': 'Arial','color':'#003948'}),
                    html.Div(children=[ dcc.Dropdown(
                                        id="selected_country",
                                        options = [{'label': 'Taiwan', 'value': 'TW'},
                                                {'label': 'Singapore', 'value': 'SG'},
                                                ],
                                        value = 'TW',
                                        multi=False,
                                        style={'font-family': 'Arial','width':'70 %'},
                    )],style={'font-family': 'Arial','min-width':'70%'})] ,style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
                html.Div(children=[
                    html.H4('Site Name',style={'font-family': 'Arial','color':'#003948'}),
                      html.Div(children=[ dcc.Dropdown(
                    id="selected_whname",
                    options = [{'label': 'DC1', 'value': 'Dayuan DC1'},
                            {'label': 'DC2', 'value': 'Dayuan DC2'},
                            ],
                    value = 'Dayuan DC1',   
                    multi=False,)],style={'font-family': 'Arial','min-width':'70%'})] ,style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
                html.Div(children=[
                    html.H4('Plan Code',style={'font-family': 'Arial','color':'#003948'}),
                    html.Div(children=[   dcc.Dropdown(
                    id="selected_plancode",
                    options = [{'label': '2810', 'value': '2810'},
                            {'label': '2811', 'value': '2811'},
                            ],
                    value = '2810',
                    multi=False,
                  )],style={'font-family': 'Arial','min-width':'70%'})] ,style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
            ],style={'font-family': 'Arial','display': 'grid', 'grid-auto-columns': '1fr',' grid-template-rows': '30% 30% 30%','gap': '0px 0px','grid-area': 'Proloc'}),

            html.Div(id="Probias",children=[
                  html.Div(children=[
                                        html.H2('Project Bias',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),
                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','background':'#005d62'}), 
                    html.Div(children=[
                        html.H4('Project Type',style={'font-family': 'Arial','color':'#003948'}),
                         html.Div(children=[           dcc.Dropdown(
                                        id="projecttype",
                                        options=[
                                                    {"label": i, "value": i}for i in range(1,13)
                                                ],
                                        value = '1',
                                        multi=False,
                                    )
                         ],style={'font-family': 'Arial','min-width':'70%'}),
                           ] ,style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
                    html.Div(children=[
                        html.H4('Duration of Analysis (months):',style={'font-family': 'Arial','color':'#003948'}),
                        html.Div(children=[             dcc.Dropdown(
                            id="slct_month",
                            options=[
                                        {"label": i, "value": i}
                                        for i in range(1,13)
                                    ],
                            value = '1',
                            multi=False,
                            style={'font-family': 'Arial','width':'70 %'},
                             ) ],style={'font-family': 'Arial','min-width':'70%'}),] ,style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
                    html.Div(children=[
                        html.H4('Projected Growth Years:',style={'font-family': 'Arial','color':'#003948'}),
                         html.Div(children=[        dcc.Dropdown(
                            id="slct_year",
                            style={'font-family': 'Arial','width':'70 %'},
                            options=[
                                        {"label": i, "value": i}
                                        for i in range(1,11)
                                    ],
                                value = 5,
                                multi=False,
                             )],style={'font-family': 'Arial','min-width':'70%'}),] ,style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
            ],style={'font-family': 'Arial','display': 'grid', 'grid-auto-columns': '1fr',' grid-template-rows': '30% 30% 30%','gap': '0px 0px','grid-area': 'Probias'}),
        

            html.Div(id="Siteinput",children=[
               
                html.Div(children=[
                                        html.H2('Site Input Parameters',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),
                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','background':'#005d62'}), 
                        
                    html.Div(children=[
                        html.H4('No of Inbound Docking Areas',style={'font-family': 'Arial','color':'#003948'}),
                        dcc.Input(
                            id='No of Inbound Docking Areas',
                            placeholder='Input Space Area (sqm)',
                            type='number',
                            value='100',
                        ),
                        html.H4('No of Outbound Docking Areas',style={'font-family': 'Arial','color':'#003948'}),
                    dcc.Input(
                        id='No of Outbound Docking Areas',
                        placeholder='Input Space Area (sqm)',
                        type='number',
                        value='10000',),
                        ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),

                    html.Div(children=[
                        html.H4('Inbound Staging Area (sqm)',style={'font-family': 'Arial','color':'#003948'}),
                        dcc.Input(
                            id='Inbound Staging Area (sqm)',
                            placeholder='Input Staging Area (sqm)',
                            type='number',
                            value='100',
                        ),
                        html.H4('Outbound Staging Area (sqm)',style={'font-family': 'Arial','color':'#003948'}),
                    dcc.Input(
                        id='Outbound Staging Area (sqm)',
                        placeholder='Input Staging Area (sqm)',
                        type='number',
                        value='10000',),
                        ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),

                    html.Div(children=[
                        html.H4('Inbound Office Area (sqm)',style={'font-family': 'Arial','color':'#003948'}),
                        dcc.Input(
                            id='Inbound Office Area (sqm)',
                            placeholder='Input Office Area (sqm)',
                            type='number',
                            value='100',
                        ),
                        html.H4('Outbound Office Area (sqm)',style={'font-family': 'Arial','color':'#003948'}),
                    dcc.Input(
                        id='Outbound Office Area (sqm)',
                        placeholder='Input Ofiice Area (sqm)',
                        type='number',
                        value='10000',),
                        ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','justify-content': 'space-between','grid-area': 'Siteinput'}), 
        

   
            html.Div(id="AreaBias",children=[
                            html.Div(children=[
                                        html.H2('Storage Area',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),
                                        html.H2('Aircon',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),
                                        html.H2('Non Aircon',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),
                                        html.H2('Cold Room',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),
                                        html.H2('Freezer',style={'font-family': 'Arial','background-color':'#005d62','color':'White'}),

                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','background':'#005d62'}), 
                        
                            html.Div(children=[
                                html.H4('Floor Area (sqm)',id='Floorarea',style={'font-family': 'Arial','color':'#003948'}),
                                dcc.Input(
                                    id='ACspace',
                                    placeholder='Input Space Area (sqm)',
                                    type='number',
                                    value='10000',
                                ),
                            dcc.Input(
                                id='NACspace',
                                placeholder='Input Space Area (sqm)',
                                type='number',
                                value='10000',
                            ),
                            dcc.Input(
                                id='COspace',
                                placeholder='Input Space Area (sqm)',
                                type='number',
                                value='1000',
                            ),dcc.Input(
                                id='FZspace',
                                placeholder='Input Space Area (sqm)',
                                type='number',
                                value='300',
                            ),
                    ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
                            
                            html.Div(children=[
                                            html.H4('Height (m)',id='Height',style={'font-family': 'Arial','color':'#003948'}),
                                            dcc.Input(
                                                id='ACheight',
                                                placeholder='Input warehouse height (m)',
                                                type='number',

                                                value='12',
                                            ),
                                            dcc.Input(
                                            id='NACheight',
                                            placeholder='Input warehouse height (m)',
                                            type='number',
                                            value='12',
                                                    ),
                                                        
                                        dcc.Input(
                                            id='COheight',
                                            placeholder='Input warehouse height (m)',
                                            type='number',
                                            value='3',
                                        ),
                                        
                                        dcc.Input(
                                            id='FZheight',
                                            placeholder='Input warehouse height (m)',
                                            type='number',
                                            value='3',
                                        ),    

                                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),
                                        
                            html.Div(children=[
                                            html.H4('Staging (sqm)',id='Staging',style={'font-family': 'Arial','color':'#003948'}),
                                            dcc.Input(
                                                id='ACstaging',
                                                placeholder='Input warehouse height (m)',
                                                type='number',
                                                value='3',
                                            ),   
                                        dcc.Input(
                                            id='NACstaging',
                                            placeholder='Input warehouse height (m)',
                                            type='number',
                                            value='3',
                                        ),   
                                        dcc.Input(
                                            id='COstaging',
                                            placeholder='Input warehouse height (m)',
                                            type='number',
                                            value='3',
                                        ),   
                                        dcc.Input(
                                            id='FZstaging',
                                            placeholder='Input warehouse height (m)',
                                            type='number',
                                            value='3',
                                        ),   
                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-between','align-items': 'center'}),        
            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','justify-content': 'space-between','grid-area': 'AreaBias'}), 
        ],style={'font-family': 'Arial',                        'display': 'grid',
                                            'grid-auto-columns': '1fr',
                                            'grid-template-columns': '30% 70%',
                                            'grid-template-rows': '50% 50%',
                                            'gap': '5px 5px',
                                            'grid-template-areas': 
                                                '"Proloc Siteinput""Probias AreaBias"',
                                                'padding': '5px'}),]),                
        html.Br(),
        dcc.Tabs(children=[
            dcc.Tab(label='Storage Space: Pallet Growth Requirements', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div([    html.Div([ html.H4('Warehouse Condition',style={'font-family': 'Arial','color':'#003948'}),
                                                        dcc.Dropdown(id="slct_ware",
                                                            options=[{'label': i, 'value': i} for i in conditionlist],
                                                            value="AC",
                                                            multi=False,
                                                            style={'font-family': 'Arial','min-width': "40%",},),
                                                        html.H4('Storage UOM',style={'font-family': 'Arial','color':'#003948'}),
                                                        dcc.Dropdown(id="slct_storage",
                                                              options = [{'label': 'Pallet', 'value': 'Pallet'},
                                                                         {'label': 'Bin', 'value': 'Bin'},],
                                                            value="Pallet",
                                                            multi=False,
                                                            style={'font-family': 'Arial','min-width': "40%",},)],style={'display': 'flex','flex-direction': 'row','justify-content': 'space-evenly','align-items': 'center','min-width':'100%'}),
                                                            dcc.Graph(id='graph2', figure={},style={'font-family': 'Arial','padding':'10px','min-width':'100%'}),
                                                            ],style={'font-family': 'Arial','padding':'10px','min-width':'100%','display': 'flex','flex-direction': 'column','justify-content': 'space-evenly','align-items': 'center'}),
               
             ]), 
            dcc.Tab(label='Inventory Profile: Number of Pallets per Batch', style=tab_style, selected_style=tab_selected_style,children=[
                                                       html.Div([html.Div([html.H4('Warehouse Condition',style={'font-family': 'Arial','color':'#003948'}),
                                                        dcc.Dropdown(id="slct_impact2",
                                                            options=[{'label': i, 'value': i} for i in conditionlist],
                                                            value="AC",
                                                            multi=False,
                                                            style={'font-family': 'Arial','min-width': "40%",},),
                                                            html.H4('Product Type',style={'font-family': 'Arial','color':'#003948'}),
                                                        dcc.Dropdown(id="slct_impact",
                                                            options=[{'label': i, 'value': i} for i in projectlist],
                                                            value="Vaccine",
                                                            multi=False,
                                                            placeholder="Product Type",
                                                             style={'font-family': 'Arial','min-width': "40%",}
                                                            ),],style={'font-family': 'Arial','padding':'10px','min-width':'100%','display': 'flex','flex-direction': 'row','justify-content': 'space-evenly','align-items': 'center'}),
                                                        
                                                        dcc.Graph(id='graph', figure={},style={'min-width':'100%','font-family': 'Arial','grid-area': 'Noperballet'}),
                                                        ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','min-width':'100%',}), 
                                                         ]), 
        dcc.Tab(label='Order Profile: Slotting analysis', style=tab_style, selected_style=tab_selected_style,children=[
                      html.Div([html.Div([           html.H4('Warehouse Condition',style={'font-family': 'Arial','color':'#003948'}),
                                                        dcc.Dropdown(id="slct_profile_warehouse",
                                                            options=[{'label': i, 'value': i} for i in profileconditionlist],
                                                            value="AC",
                                                            multi=False,
                                                            style={'font-family': 'Arial','min-width': "40%",},),       
                                                            html.H4('Product Type',style={'font-family': 'Arial','color':'#003948'}),
                                                            dcc.Dropdown(id="slct_profile_product",
                                                            options=[{'label': i, 'value': i} for i in profileprojectlist],
                                                            value="Vaccine",
                                                            multi=False,
                                                            placeholder="Product Type",
                                                             style={'font-family': 'Arial','min-width': "40%",}
                                                            ),],style={'font-family': 'Arial','padding':'10px','min-width':'100%','display': 'flex','flex-direction': 'row','justify-content': 'space-evenly','align-items': 'center'}),
                      html.Div([     
                        dcc.Graph(id='graph6', figure={},style={'font-family': 'Arial','max-width':'30%'}),
                        ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-around'}),
                         ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','min-width':'100%',}), 
                     ]),
            dcc.Tab(label='Order Profile: ABC Velocity', style=tab_style, selected_style=tab_selected_style,children=[
                     
                      html.Div([     
                        dcc.Graph(id='graph3', figure={},style={'font-family': 'Arial','max-width':'30%'}),
                        dcc.Graph(id='graph4', figure={},style={'font-family': 'Arial','max-width':'30%'}), 
                        dcc.Graph(id='graph5', figure={},style={'font-family': 'Arial','max-width':'30%'}), 
                        ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-around'}),
                     ]),

            dcc.Tab(label='Storage System Recommendations', style=tab_style, selected_style=tab_selected_style,children=[
                html.Div([     
                                     html.Div(id="tableACB",style={'font-family': 'Arial','max-width':'30%'}), 
                                     html.Div(id="tableAC",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableFZB",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableCOB",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableCOP",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableACB2",style={'font-family': 'Arial','max-width':'30%'}), 
                                     html.Div(id="tableAC2",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableFZB2",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableCOB2",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableCOP2",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableACB3",style={'font-family': 'Arial','max-width':'30%'}), 
                                     html.Div(id="tableAC3",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableFZB3",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableCOB3",style={'font-family': 'Arial','max-width':'30%'}),
                                      html.Div(id="tableCOP3",style={'font-family': 'Arial','max-width':'30%'}),
                            ],style={'display':'none'}),
                            html.Div([ 
                                    html.Div([     
                                      html.Div(id="tableArea",style={'font-family': 'Arial','display': 'inline-block'}),
                                      
                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-evenly'}),
                              
                                      
                           dcc.Tabs([  
                                              
                                    dcc.Tab(label='Recommendations system 1', style=tab_style, selected_style=tab_selected_style,children=[html.Div(id="expands", style={'font-family': 'Arial','display': 'inline','max-width':'30%',}),]),       
                                    dcc.Tab(label='Recommendations system 2', style=tab_style, selected_style=tab_selected_style,children=[html.Div(id="expands2", style={'font-family': 'Arial','display': 'inline','max-width':'30%',}),]),
                                    dcc.Tab(label='Recommendations system 3', style=tab_style, selected_style=tab_selected_style,children=[html.Div(id="expands3", style={'font-family': 'Arial','display': 'inline','max-width':'30%',}),])
                                      
                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'row','justify-content': 'space-evenly'}),
                            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','min-width':'100%'}),
                        ]),
        ], style=tabs_styles),    
         
        ])
        
    #expand
    @app.callback(
        dash.dependencies.Output("tableArea","children"),
        [dash.dependencies.Input("ACheight","value")]
    )
    # calculate Total
    def calAreatotal(area):
        dfAreatem=dfArea.drop_duplicates()
        dfAreatem['id'] = dfAreatem.index
        dfAreatem.set_index('id', inplace=True, drop=False)

        dfAreatem2=dfArea2.drop_duplicates()
        dfAreatem2['id'] = dfAreatem2.index
        dfAreatem2.set_index('id', inplace=True, drop=False)

        dfAreatem3=dfArea3.drop_duplicates()
        dfAreatem3['id'] = dfAreatem3.index
        dfAreatem3.set_index('id', inplace=True, drop=False)
        return html.Div([
            html.Div(children=[
              html.H4('Recommendations system 1',style={'font-family': 'Arial','color':'#003948'}),
            dash_table.DataTable(
                id='datatable',
                data=dfAreatem.to_dict('records'),
                columns=[{"name": i, "id": i} for i in dfAreatem.columns if i != 'id'],
                row_selectable='single',
                style_table={'min-width': '30%'})
            ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','max-width': '33%'}),
            html.Div(children=[
            html.H4('Recommendations system 2',style={'font-family': 'Arial','color':'#003948'}),
        
            dash_table.DataTable(
                id='datatable2',
                data=dfAreatem2.to_dict('records'),
                columns=[{"name": i, "id": i} for i in dfAreatem2.columns if i != 'id'],
                row_selectable='single',
                style_table={'min-width': '30%'}
            ),
             ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','max-width': '33%'}),
            html.Div(children=[
            html.H4('Recommendations system 3',style={'font-family': 'Arial','color':'#003948'}),
        
            dash_table.DataTable(
                id='datatable3',
                data=dfAreatem3.to_dict('records'),
                columns=[{"name": i, "id": i} for i in dfAreatem3.columns if i != 'id'],
                row_selectable='single',
                style_table={'min-width': '30%'}
            ),
             ],style={'font-family': 'Arial','display': 'flex','flex-direction': 'column','max-width': '30%'}),
        ],style={'display':'flex','flex-direction': 'row','justify-content': 'space-evenly'},)

    


    @app.callback(
        Output('expands', 'children'),
        Input('datatable', 'selected_row_ids'),
        )
    def expands(selected_row_ids):
        if selected_row_ids!=None :
            dfareateam=dfArea.drop_duplicates()
            storage=dfareateam.loc[[selected_row_ids[0]],['StorageUOM']].values.tolist()[0][0]
            warehouse=dfareateam.loc[[selected_row_ids[0]],['WarehouseStorageCondition']].values.tolist()[0][0]
            if storage == 'Pallet' :
                if warehouse =='Aircon':
                    table= html.Div(id="tableAC",style={'font-family': 'Arial','display': 'inline-block'})
                elif warehouse =='Cold Room':
                    table= html.Div(id="tableCOP",style={'font-family': 'Arial','display': 'inline-block'}),
                else :
                    table= html.H3("No Such data found!")
            elif storage == 'Bin' :
                if warehouse =='Aircon':
                    table= html.Div(id="tableACB",style={'font-family': 'Arial','display': 'inline-block'}),     
                elif warehouse =='Freezer':
                    table= html.Div(id="tableFZB",style={'font-family': 'Arial','display': 'inline-block'}),
                else :
                    table= html.Div(id="tableCOB",style={'font-family': 'Arial','display': 'inline-block'}),
            else :
                table= html.H3("Refresh page to obtain Table")
        else : table = html.H3(" ")
        return table
   
    @app.callback(
        Output('expands2', 'children'),
        Input('datatable2', 'selected_row_ids'),
        )
    def expands(selected_row_ids):
        if selected_row_ids!=None :
            dfareateam=dfArea2.drop_duplicates()
            storage=dfareateam.loc[[selected_row_ids[0]],['StorageUOM']].values.tolist()[0][0]
            warehouse=dfareateam.loc[[selected_row_ids[0]],['WarehouseStorageCondition']].values.tolist()[0][0]
            if storage == 'Pallet' :
                if warehouse =='Aircon':
                    table= html.Div(id="tableAC2",style={'font-family': 'Arial','display': 'inline-block'})
                elif warehouse =='Cold Room':
                    table= html.Div(id="tableCOP2",style={'font-family': 'Arial','display': 'inline-block'}),
                else :
                    table= html.H3("No Such data found!")
            elif storage == 'Bin' :
                if warehouse =='Aircon':
                    table= html.Div(id="tableACB2",style={'font-family': 'Arial','display': 'inline-block'}),     
                elif warehouse =='Freezer':
                    table= html.Div(id="tableFZB2",style={'font-family': 'Arial','display': 'inline-block'}),
                else :
                    table= html.Div(id="tableCOB2",style={'font-family': 'Arial','display': 'inline-block'}),
            else :
                table= html.H3("Refresh page to obtain Table")
        else : table = html.H3(" ")
        return table
    @app.callback(
        Output('expands3', 'children'),
        Input('datatable3', 'selected_row_ids'),
        )
    def expands(selected_row_ids):
        if selected_row_ids!=None :
            dfareateam=dfArea3.drop_duplicates()
            storage=dfareateam.loc[[selected_row_ids[0]],['StorageUOM']].values.tolist()[0][0]
            warehouse=dfareateam.loc[[selected_row_ids[0]],['WarehouseStorageCondition']].values.tolist()[0][0]
            if storage == 'Pallet' :
                if warehouse =='Aircon':
                    table= html.Div(id="tableAC3",style={'font-family': 'Arial','display': 'inline-block'})
                elif warehouse =='Cold Room':
                    table= html.Div(id="tableCOP3",style={'font-family': 'Arial','display': 'inline-block'}),
                else :
                    table= html.H3("No Such data found!")
            elif storage == 'Bin' :
                if warehouse =='Aircon':
                    table= html.Div(id="tableACB3",style={'font-family': 'Arial','display': 'inline-block'}),     
                elif warehouse =='Freezer':
                    table= html.Div(id="tableFZB3",style={'font-family': 'Arial','display': 'inline-block'}),
                else :
                    table= html.Div(id="tableCOB3",style={'font-family': 'Arial','display': 'inline-block'}),
            else :
                table= html.H3("Refresh page to obtain Table")
        else : table = html.H3(" ")
        return table
   


    @app.callback(
        [ 
        Output(component_id='graph', component_property='figure'),
        Output(component_id='graph2', component_property='figure'),
        Output(component_id='graph3', component_property='figure'),
        Output(component_id='graph4', component_property='figure'),
        Output(component_id='graph5', component_property='figure'),
        Output(component_id='graph6', component_property='figure'),
        ],
        [    
        Input(component_id='slct_impact', component_property='value'),
        Input(component_id='slct_year', component_property='value'),
        Input(component_id='slct_impact2', component_property='value'),
        Input(component_id='slct_profile_product', component_property='value'),
        Input(component_id='slct_profile_warehouse', component_property='value'),
        Input(component_id='slct_ware', component_property='value'),
        Input(component_id='slct_storage', component_property='value'),
        
        ])
    def update_graph(option_slctd,option_slcted2,option_slcted3,option_slcted4,option_slcted5,option_slcted6,option_slcted7):#,option_slcted3
        dff = bm.copy()
        dff["ProductType"]=dff["ProductType"].astype("string")
        dff["WarehouseStorageCondition"]=dff["WarehouseStorageCondition"].astype("string")
        dff = dff.loc[ dff["ProductType"]== option_slctd] 
        dff = dff.loc[ dff["WarehouseStorageCondition"]== option_slcted3] 
        fig = px.bar(
            width=800, height=400,
            data_frame=dff,
            x='Batch',
            y='%',
            hover_data=['Batch', '%'],
            labels={'Batch': 'Number of Pallet Per Batch'})
        
            # template='plotly_dark'
        fig.update_layout( autosize=True,
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell")
        )
        dff2= spt.copy()
        dff2=dff2[(dff2["StorageUOM"] == option_slcted7) &(dff2['WarehouseStorageCondition']==option_slcted6)]
        dff2=dff2.iloc[:,[2,3,4,5,6,7,8,9,10,11,12]]
        Products=list(dff2.ProductType.unique())
        dff2.rename(columns={"Pallet Quantity":'2021'}, inplace=True)
        Rowcount=len(dff2.index)
        dff2=dff2.T

        new_header = dff2.iloc[0] #grab the first row for the header
        dff2 = dff2[1:] #take the data less the header row
        dff2.columns = new_header
        dff2.reset_index(inplace=True)
        dff2=dff2.head(option_slcted2)
        layout = go.Layout(xaxis=dict(autorange=True,automargin=True), title="Pallet Quantity VS Years",
        xaxis_title="Years",
        yaxis_title="PalletQuantity")
        fig2= go.Figure(layout=layout)
        dff2['Total'] = dff2.drop('index',axis=1).sum(axis=1)
        for column in dff2:
            if column!="index" and column!="Total":
                fig2.add_trace(go.Bar(name=column,x=dff2['index'],y=dff2[column]))
        fig2.update_layout(barmode='stack')
        fig2.add_trace(go.Scatter(x=dff2['index'], y=dff2['Total'], mode='lines+markers',name='Total'))
        fig2.update_layout(margin=dict(t=50, b=0, l=0, r=0))
        fig3 = px.pie(abc_ac, values='HIT%', hole=.5, names='ABC_CLASS',title='ABC_CLASS_Aircon')
        fig4 = px.pie(abc_co, values='HIT%',  hole=.5,names='ABC_CLASS',title='ABC_CLASS_ColdRoom')
        fig5 = px.pie(abc_fz, values='HIT%', hole=.5, names='ABC_CLASS',title='ABC_CLASS_Freezer')
        fig3.update_layout(margin=dict(t=50, b=0, l=0, r=0))
        fig4.update_layout(margin=dict(t=50, b=0, l=0, r=0))
        fig5.update_layout(margin=dict(t=50, b=0, l=0, r=0))


        dff = orderprofile.copy()
        dff["ProductType"]=dff["ProductType"].astype("string")
        dff["WarehouseStorageCondition"]=dff["WarehouseStorageCondition"].astype("string")
        dff = dff.loc[ dff["ProductType"]== option_slcted4] 
        dff=dff.drop("ProductType",axis=1)
        dff_ac = dff.loc[dff["WarehouseStorageCondition"]== option_slcted5] 
        def prepocess(dataframe) :
            dftem=dataframe.T
            dftem.columns = dftem.iloc[0]
            dftem = dftem[1:]
            
            return dftem
        try:
            fig6 = px.pie(prepocess(dff_ac), values=option_slcted5, hole=.5, names=prepocess(dff_ac).index,title='Slotting Analysis')
            fig6.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        except:
            fig6 = px.pie(None, values=None, names=None,title='No Data found under this criteria!')
        return  fig, fig2,fig3,fig4,fig5,fig6


   
    ######################Reco 1
    @app.callback(
        dash.dependencies.Output("tableAC","children"),
        [dash.dependencies.Input("ACheight","value")]
    )
    # calculate Aicron pallet area
    def calAreaAC(acheight):
        wh_height=float(acheight)

        def requireAreaAC(row,i):
            if row["Recommend System"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
        
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=4
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Double Deep Racking (DDR)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Shuttle Storage System']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=1.5
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            else:
                area=0
            return area
        p_AC_R1['Area(sqm)'] = p_AC_R1.apply(lambda row: int(requireAreaAC(row,wh_height)) , axis=1)
        total = p_AC_R1['Area(sqm)'].sum()
        dfArea.loc[len(dfArea.index)]=['Aircon','Pallet',total]
        dfArea.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=p_AC_R1.to_dict('records'),
                columns=[{"name": i, "id": i} for i in p_AC_R1.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in p_AC_R1.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            
            html.H2("Total Area need is"+str(total)+"square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})
    
    @app.callback(
        dash.dependencies.Output("tableCOP","children"),
        [dash.dependencies.Input("COheight","value")]
    )
    #calculate Coldroom pallet area
    def calAreaCOP(coheight):
        wh_height=float(coheight)

        def requireAreaCO(row,i):
            if row["Recommend System"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
                
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=4
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Double Deep Racking (DDR)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Shuttle Storage System']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=1.5
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            else:
                area=0
            return area
        p_CO_R1['Area(sqm)'] = p_CO_R1.apply(lambda row: int(requireAreaCO(row,wh_height)) , axis=1)
        total = p_CO_R1['Area(sqm)'].sum()
        dfArea.loc[len(dfArea.index)]=['Cold room','Pallet',total]
        dfArea.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=p_CO_R1.to_dict('records'),
                columns=[{"name": i, "id": i} for i in p_CO_R1.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in p_CO_R1.to_dict('records')
                ],
        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableACB","children"),
        [dash.dependencies.Input("ACheight","value")]
    )
    #calculate Aircon Bin area
    def calAreaACB(acheight):
        wh_height=float(acheight)
        def requireAreaACB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area
        b_AC_R1['Area(sqm)'] = b_AC_R1.apply(lambda row: int(requireAreaACB(row,wh_height)) , axis=1)
        total = b_AC_R1['Area(sqm)'].sum()
        dfArea.loc[len(dfArea.index)]=['Aircon','Bin',total]
        dfArea.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_AC_R1.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_AC_R1.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_AC_R1.to_dict('records')
                ],

        tooltip_delay=0,
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableCOB","children"),
        [dash.dependencies.Input("COheight","value")]
    )
    #calculate Cold room Bin area
    def calAreaCOB(coheight):
        wh_height=float(coheight)

        def requireAreaCOB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area
        b_CO_R1['Area(sqm)'] = b_CO_R1.apply(lambda row: int(requireAreaCOB(row,wh_height)) , axis=1)
        total = b_CO_R1['Area(sqm)'].sum()
        dfArea.loc[len(dfArea.index)]=['Cold room','Bin',total]
        dfArea.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_CO_R1.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_CO_R1.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_CO_R1.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableFZB","children"),
        [dash.dependencies.Input("FZheight","value")]
    )
    #calculate Freezer room Bin area
    def calAreaFZB(fzheight):
        wh_height=float(fzheight)

        def requireAreaFZB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area
        b_FZ_R1['Area(sqm)'] = b_FZ_R1.apply(lambda row: int(requireAreaFZB(row,wh_height)) , axis=1)
        total = b_FZ_R1['Area(sqm)'].sum()
        dfArea.loc[len(dfArea.index)]=['Freezer','Bin',total]
        dfArea.drop_duplicates()
       
        return html.Div([
            dash_table.DataTable(
                data=b_FZ_R1.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_FZ_R1.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_FZ_R1.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})
    
    ######################################reco2
    @app.callback(
        dash.dependencies.Output("tableAC2","children"),
        [dash.dependencies.Input("ACheight","value")]
    )
    def calAreaAC2(acheight):
        wh_height=float(acheight)

        def requireAreaAC(row,i):
            if row["Recommend System"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
        
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=4
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Double Deep Racking (DDR)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Shuttle Storage System']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=1.5
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            else:
                area=0
            return area
        p_AC_R2['Area(sqm)'] = p_AC_R2.apply(lambda row: int(requireAreaAC(row,wh_height)) , axis=1)
        total = p_AC_R2['Area(sqm)'].sum()
        dfArea2.loc[len(dfArea2.index)]=['Aircon','Pallet',total]
        dfArea2.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=p_AC_R2.to_dict('records'),
                columns=[{"name": i, "id": i} for i in p_AC_R2.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in p_AC_R2.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            
            html.H2("Total Area need is"+str(total)+"square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})
    
    @app.callback(
        dash.dependencies.Output("tableCOP2","children"),
        [dash.dependencies.Input("COheight","value")]
    )
    #calculate Coldroom pallet area
    def calAreaCOP2(coheight):
        wh_height=float(coheight)

        def requireAreaCO(row,i):
            if row["Recommend System"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
                
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=4
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Double Deep Racking (DDR)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Shuttle Storage System']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=1.5
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            else:
                area=0
            return area
       
        p_CO_R2['Area(sqm)'] = p_CO_R2.apply(lambda row: int(requireAreaCO(row,wh_height)) , axis=1)
        total = p_CO_R2['Area(sqm)'].sum()
        dfArea2.loc[len(dfArea2.index)]=['Cold room','Pallet',total]
        dfArea2.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=p_CO_R2.to_dict('records'),
                columns=[{"name": i, "id": i} for i in p_CO_R2.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in p_CO_R2.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableACB2","children"),
        [dash.dependencies.Input("ACheight","value")]
    )
    #calculate Aircon Bin area
    def calAreaACB2(acheight):
        wh_height=float(acheight)
        def requireAreaACB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area

        b_AC_R2['Area(sqm)'] = b_AC_R2.apply(lambda row: int(requireAreaACB(row,wh_height)) , axis=1)
        total = b_AC_R2['Area(sqm)'].sum()
        dfArea2.loc[len(dfArea2.index)]=['Aircon','Bin',total]
        dfArea2.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_AC_R2.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_AC_R2.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_AC_R2.to_dict('records')
                ],

        tooltip_delay=0,
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableCOB2","children"),
        [dash.dependencies.Input("COheight","value")]
    )
    #calculate Cold room Bin area
    def calAreaCOB2(coheight):
        wh_height=float(coheight)

        def requireAreaCOB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area

        b_CO_R2['Area(sqm)'] = b_CO_R2.apply(lambda row: int(requireAreaCOB(row,wh_height)) , axis=1)
        total = b_CO_R2['Area(sqm)'].sum()
        dfArea2.loc[len(dfArea2.index)]=['Cold room','Bin',total]
        dfArea2.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_CO_R2.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_CO_R2.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_CO_R2.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableFZB2","children"),
        [dash.dependencies.Input("FZheight","value")]
    )
    #calculate Freezer room Bin area
    def calAreaFZB2(fzheight):
        wh_height=float(fzheight)

        def requireAreaFZB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area

        b_FZ_R2['Area(sqm)'] = b_FZ_R2.apply(lambda row: int(requireAreaFZB(row,wh_height)) , axis=1)
        total = b_FZ_R2['Area(sqm)'].sum()
        dfArea2.loc[len(dfArea2.index)]=['Freezer','Bin',total]
        dfArea2.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_FZ_R2.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_FZ_R2.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_FZ_R2.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})
   ######################################reco3
    @app.callback(
        dash.dependencies.Output("tableAC3","children"),
        [dash.dependencies.Input("ACheight","value")]
    )
    def calAreaAC3(acheight):
        wh_height=float(acheight)

        def requireAreaAC(row,i):
            if row["Recommend System"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
        
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=4
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Double Deep Racking (DDR)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Shuttle Storage System']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=1.5
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            else:
                area=0
            return area
        p_AC_R3['Area(sqm)'] = p_AC_R3.apply(lambda row: int(requireAreaAC(row,wh_height)) , axis=1)
        total = p_AC_R3['Area(sqm)'].sum()
        dfArea3.loc[len(dfArea3.index)]=['Aircon','Pallet',total]
        dfArea3.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=p_AC_R3.to_dict('records'),
                columns=[{"name": i, "id": i} for i in p_AC_R3.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in p_AC_R3.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            
            html.H2("Total Area need is"+str(total)+"square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})
    
    @app.callback(
        dash.dependencies.Output("tableCOP3","children"),
        [dash.dependencies.Input("COheight","value")]
    )
    #calculate Coldroom pallet area
    def calAreaCOP3(coheight):
        wh_height=float(coheight)

        def requireAreaCO(row,i):
            if row["Recommend System"]in['Selective Pallet Racking (SPR)','Ground Storage','Drive-Through Rack','Drive-In Rack','Mobile Rack'] :
                
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=4
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Very Narrow Ailse (VNA) & Truck','Automatic Storage Retrieval System (ASRS)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Double Deep Racking (DDR)']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=2.8
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//4)*(wh_length-0.3)*(0.8*4+aisle+0.3)+(lef//onebay*2.7*0.8) 
            elif row["Recommend System"]in['Shuttle Storage System']:
                wh_length=100
                p_height=1.8
                p_width=0.8
                p_length=1.2
                aisle=1.5
                level=i //(p_height+0.4)
                onebay=level*3
                num=(wh_length-0.3)//2.8
                sum_1=num*level*3
                if row["Quantity"] <= onebay:
                    area=2.7*0.8
                elif row["Quantity"]<= sum_1:
                    num2=int(row["Quantity"]/onebay)
                    area=num2*2.7*0.8
                elif row["Quantity"]> sum_1: 
                    no_bay=row["Quantity"]//sum_1
                    lef=row["Quantity"]%sum_1
                    if no_bay<2:
                        area= no_bay*(wh_length-0.3)*0.8+(lef//onebay*2.7*0.8)
                    else:
                        area=(no_bay//2)*(wh_length-0.3)*(0.8*2+aisle+0.3)+(lef//onebay*2.7*0.8) 
            else:
                area=0
            return area
       
        p_CO_R3['Area(sqm)'] = p_CO_R3.apply(lambda row: int(requireAreaCO(row,wh_height)) , axis=1)
        total = p_CO_R3['Area(sqm)'].sum()
        dfArea3.loc[len(dfArea3.index)]=['Cold room','Pallet',total]
        dfArea3.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=p_CO_R3.to_dict('records'),
                columns=[{"name": i, "id": i} for i in p_CO_R3.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in p_CO_R3.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableACB3","children"),
        [dash.dependencies.Input("ACheight","value")]
    )
    #calculate Aircon Bin area
    def calAreaACB3(acheight):
        wh_height=float(acheight)
        def requireAreaACB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area

        b_AC_R3['Area(sqm)'] = b_AC_R3.apply(lambda row: int(requireAreaACB(row,wh_height)) , axis=1)
        total = b_AC_R3['Area(sqm)'].sum()
        dfArea3.loc[len(dfArea3.index)]=['Aircon','Bin',total]
        dfArea3.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_AC_R3.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_AC_R3.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_AC_R3.to_dict('records')
                ],

        tooltip_delay=0,
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableCOB3","children"),
        [dash.dependencies.Input("COheight","value")]
    )
    #calculate Cold room Bin area
    def calAreaCOB3(coheight):
        wh_height=float(coheight)

        def requireAreaCOB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area

        b_CO_R3['Area(sqm)'] = b_CO_R3.apply(lambda row: int(requireAreaCOB(row,wh_height)) , axis=1)
        total = b_CO_R3['Area(sqm)'].sum()
        dfArea3.loc[len(dfArea3.index)]=['Cold room','Bin',total]
        dfArea3.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_CO_R3.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_CO_R3.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_CO_R3.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    @app.callback(
        dash.dependencies.Output("tableFZB3","children"),
        [dash.dependencies.Input("FZheight","value")]
    )
    #calculate Freezer room Bin area
    def calAreaFZB3(fzheight):
        wh_height=float(fzheight)

        def requireAreaFZB(row,i):
            if row["Recommend System"]in['Flow Rack','Shelf Rack','Bin Rack','Mobile Shelving']:
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
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['High Bay Shelf Rack']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.8
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                        area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            elif row["Recommend System"]in['Vertical Carousel Storage']:
                wh_length=100
                c_height=0.5
                c_width=0.3
                c_length=0.4
                aisle=2.5
                level=i//c_height
                s_depth=1.7
                bay=1.28
                num1=bay//c_length
                num2=s_depth//c_width
                sum_1=num1*num2*level
                bay_line=(wh_length-0.3)//bay
                no_bay=int(row["Quantity"]//sum_1+1)
                line=int(no_bay//bay_line+1)
                if row["Quantity"] <sum_1:
                    area=math.ceil(bay*s_depth)
                elif row["Quantity"] < bay_line*sum_1:
                    area=math.ceil(no_bay*bay*s_depth)
                else:
                    area=(wh_length-0.3)*line*1.7+(line-1)*aisle*wh_length
            else:
                area=0
            return area

        b_FZ_R3['Area(sqm)'] = b_FZ_R3.apply(lambda row: int(requireAreaFZB(row,wh_height)) , axis=1)
        total = b_FZ_R3['Area(sqm)'].sum()
        dfArea3.loc[len(dfArea3.index)]=['Freezer','Bin',total]
        dfArea3.drop_duplicates()
        return html.Div([
            dash_table.DataTable(
                data=b_FZ_R3.to_dict('records'),
                columns=[{"name": i, "id": i} for i in b_FZ_R3.columns],
                editable=False,
                tooltip_data=[
            {
                # (B) multiply cell value by 10 for demonstration purpose
                
                column: {'value': '{}'.format(('![image](https://raw.githubusercontent.com/Zq619/ZP-OE-Tool/main/image/'+str(value).replace(' ','%20')+'.jpg)') if column == 'Recommend System' else ''),'type': 'markdown'}for column, value in row.items()
                
            } for row in b_FZ_R3.to_dict('records')
                ],

        tooltip_delay=0,
        tooltip_duration=None
            ),
            html.H2("Total Area need is "+str(total)+" square meters")
            
        ],style={'font-family': 'Arial','display': 'inline-block'})

    def open_browser():
	    webbrowser.open_new("http://127.0.0.1:{}".format(8050))
    if __name__ == '__main__':
        Timer(1, open_browser).start()
        app.run_server(host='127.0.0.1', port=8050,debug=False)
else:
    sys.exit()