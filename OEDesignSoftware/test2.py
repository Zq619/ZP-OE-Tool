import pandas as pd
import numpy as np
dfA=pd.read_excel(r'C:\SLOTTING_TOOL\Export\ABC_8.xlsx')
#dfA no nned modify, just show the result 
dfs= pd.read_excel (r'D:\OE\StockOnHand_2810.xlsx')
df7 = pd.read_csv (r'D:\OE\2810_June_Complete1.csv')
#calculate product range output dataframe: pr
datafilter = dfs.loc[dfs['StorageBin'].str.len() == 12].reset_index()
datafilter = datafilter.rename(columns={"StorageCondition":"WarehouseStorageCondition"})
datafilter = datafilter.rename(columns={"StorageBin":"BinType"})
datafilter = datafilter.rename(columns={"MaterialGroup":"ProductType"})

pr=datafilter.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['Material']].nunique().reset_index()
#calculate number of pallet per batch and percentage, output dataframe: bn
selection=datafilter[datafilter['StorageUOM'].str.contains('Pallet')]
selection1=selection.groupby(['WarehouseStorageCondition','StorageUOM','ProductType','Pallet'])[['Batch']].count().reset_index()
selection1.set_index(['WarehouseStorageCondition','ProductType'],inplace=True)
selection1['%'] = (100*selection1['Batch']/selection1['Batch'].sum(level ='ProductType')).round(2)
b1=selection1.reset_index()
bn=b1.groupby(['WarehouseStorageCondition','StorageUOM','ProductType','Batch'])[['Pallet']].count().reset_index()
bn.set_index(['WarehouseStorageCondition','ProductType'],inplace=True)
bn['%'] = (100*bn['Pallet']/bn['Pallet'].sum(level = 'ProductType')).round(2)
bn=bn.reset_index()
bn=bn.drop(bn[(bn.Batch==0)].index)

# print(bn)
#select the number of the batch =1,2,3,4 and seperate into 4 tables.
bx=bn[bn['Batch'] == 1]
b3=bx.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b3= b3.rename(columns={"%":"Pallet/batch=1 %"})
bx2=bn[bn['Batch'] ==2 ]
b4=bx2.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b4= b4.rename(columns={"%":"Pallet/batch=2 %"})
bx3=bn[bn['Batch'] ==3 ]
b5=bx3.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b5= b5.rename(columns={"%":"Pallet/batch=3 %"})
bx4=bn[bn['Batch'] ==4 ]
b6=bx4.groupby(['WarehouseStorageCondition','ProductType','StorageUOM'])[['%']].sum().reset_index()
b6= b6.rename(columns={"%":"Pallet/batch=4 %"})
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
# count of how many WT per wharehouse order
op2=df7[['WarehouseOrderNumber','WarehouseTask']]
op2=op2.drop(op2[(op2.WarehouseOrderNumber==0)].index)
op2=op2.groupby(['WarehouseOrderNumber'])[['ProductNumber']].nunique().reset_index()

# table of los out pallet percentage
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



#function that calculate the growth
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
spt=spt.rename(columns={'Quantity':' UOM Quantity'})

# Merge all the criteria into one table as a input dataframe for recommending system
#p_inner for pallet recommend
#c_inner for carton recommend
merge=pd.merge(bm3,pr,how='inner')
merge=merge.rename(columns={"Material":"ProductRange"})
p_inner=pd.merge(m2,merge,how='inner')
p_inner = p_inner.fillna(0)
# print(p_inner)
c_inner=pd.merge(m4,pr,how='inner')
c_inner = c_inner.fillna(0)
c_inner=c_inner.rename(columns={"Material":"ProductRange"})
# print(c_inner)




#recommending system function

def sys1(row):
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
        if row['Pallet/batch=2 %']<50:
            v4=1
        else:
            v4=0

        sys1 = v1+v4+v3
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

result_b=c_inner.iloc[:,[0,1,2,3,4,5,6,7,8,9]] 
#serapte the result table based on warehousestorageCondition 
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
# Pallet in Aircon result table
t0=result_p_AC.sort_values(by='Quantity', ascending=False)
t1=t0.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]] 
t1=t1.rename(columns={"Quantity":"Pallet Quantity"})
t1=t1.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
t1['Recommend System 1']=t1.idxmax(axis=1)
t1=t1.reset_index()
t1=t1.iloc[:,[0,1,2,3,4,5,15]] 
#t1=recommendation 1
# print(t1)
##recommend 2
t2=t0.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]]
t2=t2.rename(columns={"Quantity":"Pallet Quantity"})
t2=t2.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
t2=t2.drop(['Selective Pallet Racking (SPR)'], axis = 1)
t2['Recommend System 2']=t2.idxmax(axis=1)

t2=t2.reset_index()
t2=t2.iloc[:,[0,1,2,3,4,5,14]] 
# print(t2)
## recommend 3
t3=t0.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]]
t3=t3.rename(columns={"Quantity":"Pallet Quantity"})
t3=t3.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
t3=t3.drop(['Selective Pallet Racking (SPR)'], axis = 1)
t3=t3.drop(['Very Narrow Ailse (VNA) & Truck'], axis = 1)
t3=t3.drop(['Ground Storage'], axis = 1)
t3['Recommend System 3']=t3.idxmax(axis=1)
t3=t3.reset_index()
t3=t3.iloc[:,[0,1,2,3,4,5,12]]
# print(t3)

# Pallet in ColdRoom result table
t_pco=result_p_CO.sort_values(by='Quantity', ascending=False)
t4=t_pco.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]] 
t4=t4.rename(columns={"Quantity":"Pallet Quantity"})
t4=t4.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
t4['Recommend System 1']=t4.idxmax(axis=1)
t4=t4.reset_index()
t4=t4.iloc[:,[0,1,2,3,4,5,15]] 
#t1=recommendation 1
# print(t1)
##recommend 2
t5=t_pco.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]]
t5=t5.rename(columns={"Quantity":"Pallet Quantity"})
t5=t5.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
t5=t5.drop(['Selective Pallet Racking (SPR)'], axis = 1)
t5['Recommend System 2']=t5.idxmax(axis=1)

t5=t5.reset_index()
t5=t5.iloc[:,[0,1,2,3,4,5,14]] 
# print(t5)
## recommend 3
t6=t_pco.iloc[:,[2,3,4,5,6,7,9,10,11,12,13,14,15,16,17]]
t6=t6.rename(columns={"Quantity":"Pallet Quantity"})
t6=t6.set_index(["ProductType","Pallet Quantity",'Pallet/batch=1 %','Pallet/batch=2 %','Pallet/batch=3 %','Pallet/batch=4 %'])
t6=t6.drop(['Selective Pallet Racking (SPR)'], axis = 1)
t6=t6.drop(['Very Narrow Ailse (VNA) & Truck'], axis = 1)
t6=t6.drop(['Ground Storage'], axis = 1)
t6['Recommend System 3']=t6.idxmax(axis=1)
t6=t6.reset_index()
t6=t6.iloc[:,[0,1,2,3,4,5,12]]
# print(t6)