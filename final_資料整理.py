import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import sklearn.metrics as metrics

#要先建立大表
#好像可以先用excel做好
df_final = pd.read_excel("final.xlsx")
#做階層式資料表
df_final2 = df_final.groupby([df_final['款號名稱'],df_final['工序名稱']]).mean()

#合併款號與工序名稱
product_name_final = list(df_final['款號名稱'])
work_name_final = list(df_final['工序名稱'])
new_name_final = []
for i in range(len(work_name_final)):
    new_name_final.append(str(product_name_final[i]) + '&' + str(work_name_final[i]))

#把新工作列表放入原檔案
df_new_final = df_final.drop(['款號名稱','工序名稱'], axis = 1)
df_new_final.insert(0,'工作名稱',new_name_final)


#匯入工作紀錄與考勤表
df = pd.read_excel("May1217.xlsx")
df_time = pd.read_excel("May_time.xlsx")
df_name = pd.read_excel("Name.xlsx")


#合併款號與工序名稱
product_name = list(df['款號名稱'])
work_name = list(df['工序名稱'])
new_name = []
for i in range(len(work_name)):
    new_name.append(str(product_name[i]) + '&' + str(work_name[i]))

#把新工作列表放入原檔案
df_new = df.drop(['款號名稱','工序名稱'], axis = 1)
df_new.insert(1,'工作名稱',new_name)
#df_new.to_csv('work.csv',encoding = 'utf_8_sig')


#取得一人表格
df_nameT = df_name.T
np_name = np.array(df_nameT)
name_list = np_name.tolist()
name = name_list[0]
#迴圈始
for x in range(len(name)):
    print(name[x])
    df1 = df_new[df_new['姓名'] == name[x]]
    dftemp = df1.drop(['姓名'], axis = 1)

#把工作名稱欄變成欄位名稱
    df_replace = dftemp.set_index("工作名稱")
    df_replace = df_replace.sort_index()

    df_replace = df_replace.groupby(df_replace.index).sum()
    
#轉置
    row_list = list(df_replace.iloc[0])
    df2 = pd.DataFrame(row_list)
    for i in range(1,len(df_replace)):
        row_list = list(df_replace.iloc[i])
        df2[i] = pd.Series(row_list)
   
     
#把時間加進去
##應該要做如果時間=0那天的工作要與下一天合併！
#刪除不要的空白列
    
    df_time_one = df_time[df_time["姓 名"] == name[x]]
    list_time = list(df_time_one['工作時間'])
    del_list = []
    for i in range(len(list_time)):
        j = sum(df2.iloc[i])
        if  j == 0:
            del_list.append(i)
    
    df2 = df2.drop(del_list)

#把多餘的時間加入下一天與刪除不要的時間
    for i in del_list:
        if i <= 29:
            list_time[i+1] = list_time[i] + list_time[i+1]
            list_time[i] = 0
        pd_time = pd.DataFrame(list_time)

    pd_time = pd_time.drop(del_list)
    


#修改欄位名稱
    work_name = list(df_replace.index)
    for i in range(len(work_name)):
        df2.rename(columns = { i: str(work_name[i])}, inplace = True)
    
#確認資料正確
    check = False
    while check == False :
        
#回歸分析
# Fit Ordinary Least Squares: OLS
    
        X = df2
        y = pd_time
        lm = LinearRegression()
        lm.fit(X, y)

#將結果結合工作名稱轉成一dataframe
        result = pd.DataFrame(lm.coef_)
        resultT = result.T
        work_name_temp = list(df2.columns.values)
        resultT['workname'] = pd.Series(work_name_temp)
        print(resultT)
        result_list = lm.coef_[0]
        
        
    
###1226如果係數<0，必須刪除欄與列
        time2T = pd_time.T
        time2T_list = list(time2T.iloc[0])
        need_del_work = []
        break_point = 0
        if break_point < len(result_list):
            for i in range(len(result_list)):
                if result_list[i] < 0 :
                    need_del_work.append(work_name_temp[i])
                    need_del = list(df2[work_name_temp[i]])
                    print(need_del) 
                    for j in range(len(need_del)):
                        if need_del[j] != 0:
                            time2T_list[j] = time2T_list[j] - need_del[j]
                        
                else:
                    break_point+=1
        if break_point == len(result_list):
            break          
        df3 = df2.drop(need_del_work, axis = 1)
        
    ###可是減掉一些工作之後，一個月中某些工時會是負的，所以必須刪除列(工作表)與列(工時)
        need_del_list = []
        
        for i in range(len(time2T_list)):
            if time2T_list[i] < 0 :
                need_del_list.append(i)
        df3 = df3.reset_index(drop=True)
        print(df3)
        df3.drop(need_del_list, axis = 0)
        
        pd_time2 = pd.DataFrame(time2T_list)
        pd_time = pd_time2.drop(need_del_list)
        
        df2 = df3.drop(need_del_list)
        

        
        
#把資料放進大表中：
#從大表中搜尋名字(以欄名搜尋)
#以result按列將資料放入
    
    j = 0
    while j < len(work_name_temp):
        for i in range(len(df_new_final)):
            if df_new_final.at[i,'工作名稱'] == work_name_temp[j]:
                df_new_final.at[i, name[x]] = result_list[j]
        j+=1
    print(x)
df_new_final.to_csv('1228.csv',encoding = 'utf_8_sig')
#問題在於index的工作名稱和work_name不同，因為work_name是已合併的，
#但df_final是還沒合併的，

#現在的工作是連在一起，之後必須分開
    
#df_new_final_split = pd.DataFrame(df_new_final.工作名稱.str.split('&',1).tolist(),columns = ['款號名稱','工序名稱'])


#new_index = df_new_final_split.groupby("款號名稱")
#new_index.to_csv('1228_split.csv',encoding = 'utf_8_sig')

                
    #把資料放進大表中：
    #從大表中搜尋名字(以欄名搜尋)
    #以result按列將資料放入
    


