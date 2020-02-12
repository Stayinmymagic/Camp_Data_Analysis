import pandas as pd
import pulp

#從SQL取得係數資料表
# 導入pymysql模塊
import pymssql
# 連接database
#Connecting using Windows Authentication
#conn = pymssql.connect(
#    host=r'dbhostname\myinstance',
#    user=r'companydomain\username',
#    password=PASSWORD,
#    database='DatabaseOfInterest')
conn = pymssql.connect(host="********", user="root",password="l******",database="final",charset="utf8mb4") 
# 得到一個可以執行SQL語句的光標對象
cursor = conn.cursor()
# 定義要執行的SQL語句
sql = "select * from efficiency_test" 

a= []
# 執行SQL語句
try:
    cursor.execute(sql)
    results = cursor.fetchall()    #獲取查詢的所有記錄
    
    #遍歷結果  
    for row in results :        
        temp = list(row)
        a.append(temp)
    
    df = pd.DataFrame(a,columns=['款號名稱','工序名稱','朱發利','楊小玲','黃金群','劉紅','吳則文','韓安貴','余章容','曾小嬌','廖文華','張世豔','陳維會','牟金玉','鄧俊英','高約珍','覃軍信','雷紅英','曾慶霞','郭梅','李秀英','王太容','陳文輝','杜大軍','陳開美','聶福潤','蔡鳳蓮','盧中良','代自利','朱學娥','代自容','謝吉香','何棚','程自友','劉冰瑤','李陽軍','鄭四瓊','周啟秀','黃代利','粟高富','胡紹容','康燕清','杜春','楊琴','張啟南','向春花','粟明翔','鐘傑','鐘德先','葉曉琴','龍良瓊','程孝芳','陳德碧','俞小琴','余春梅','彭聯華','歐常容','王陽芳','安明霞','王定偉','潘文花','潘文鳳','張愛國','效惠文','鄧霞','杜亞玲','李淑偉','鄒懷群','黃富英','劉祖彩','陳雙蓮','左志平','黃元玲','鐘俊澤','李美蘭','冉芬','張娟','晏慧蓮','周懷連','劉桃平','鄧勇','唐家惠','袁宗霞','陳宇','匡紅元','潘美玲','陳鳳娟','先方珍','徐自書','陳菊梅','張小敏','先大會','王滿妹','周喜紅','楊洪雲','龍丹','朱芬','陳志玉','王平友','胡木蘭','李轉玉','徐芳','塗東梅','胡體春','黎琴','郭平勇','彭蘭運','徐圓圓','藍珍靜','游萬瓊','于運英','曾得龍','吳學志','李小露','伍自英','李愛榮','胡定菊','徐開連','鐘群','冉茂芬','任榮梅','張金鳳','馮純山','李光蓮','郭家園','賀春秀','廖國香','李小儒','譚金運','萬丕中','李鳳珍','牟長兵','溫鳳華','黃結梅','于治國','牟偉','廖彩紅','王秋花','王華英','謝明菊','鄭雲祥','陳香英','鄭連幫','陳玲莉','王小萍','唐海瓊','樊安芳','賴世玉','張玉群','林倫桂','廖美榮','陳宗兵','張平','盧祥文','陳水英','朱岩山','後國鳳','王孝蓉','粟喜喜','陳冬香','袁慧嬋','薛創劍','李世俊','覃梅紅','賀秋英','彭文峰','李春秀','劉見洪','胡建仁','楊尚秀','陶菊華','屈志芳','梁香花','張家林','李三香','楊玉平','詹科','李淑珍','王飛','曾富霞','範流坪','譚茂月','標準工時'])
        
finally:   
# 關閉光標對象
    cursor.close()
# 關閉數據庫連接

    conn.close()

#線性規劃

#定義問題
prob = pulp.LpProblem("distribution",pulp.LpMinimize)

#從APP上取得的request
request = [['做版配片',5],['BALANCE',10],['ALPINE EXPEDITION 3',12]]
#從係數表取得指定的款號工序員工係數表
df_all = pd.DataFrame()
for i in range(len(request)):
    df1 = df[df['款號名稱'] == request[i][0]]
    frames = [df_all, df1]
    df_all = pd.concat(frames)
#設置索引
df_all = df_all.set_index(['款號名稱','工序名稱'])
#取得標準工時list
stan_time = list(df_all['標準工時'])
df_all = df_all.drop("標準工時", axis = 1)
#取得員工名list
name_list = list(df.columns[:180])
#款號名稱list
style = []
for i in range(len(request)):
    style.append(request[i][0])
#款號代稱
style_code = []
for i in range(len(style)):
    style_code.append('s'+str(i))
#工序代稱(須結合款號在前)
work = []
work_code = []
work_code2 = []
##先做好空的子list
for i in range(len(style)):
    work.append([])
    work_code2.append([])
##取得各款號內包含的工序數量
work_name = list(df['工序名稱'])
for i in range(len(style)):
    for j in range(len(df[df['款號名稱'] == style[i]])):
        work[i].append(work_name[j])
#製作款號與工序的代稱
for i in range(len(style)):
    for j in range(len(df[df['款號名稱'] == style[i]])):
        work_code.append('s'+str(i)+'/'+'x'+str(j))
        work_code2[i].append('s'+str(i)+'/'+'x'+str(j))        
#製作標準工時dict
stan = dict(zip(work_code, stan_time))

#製作工序dict
work_dict = {}
for i in range(len(work)):
    dict_temp = dict(zip(work_code2[i], work[i]))
    work_dict[style[i]] = dict_temp
#製作款號dict
style_dict = dict(zip(style_code, style))
#目標式
x =[]
TA = []
##a = 係數
for w in range(len(df_all)):
    a = list(df_all.iloc[w])
    
    for i in range(len(a)):
        if a[i] != 0:
            a[i] = round(a[i],3)
            TA.append(a[i])
            x.append(work_code[w]+'/'+str(i))
efficiency = dict(zip(x, TA))
##建立變數
num_vars = pulp.LpVariable.dicts("num",x,0)

##建立目標式
prob += pulp.lpSum([efficiency[i]*num_vars[i] for i in x])

#限制式
##限制式一：每個工序數量要相同
same =[]
num = 0
for i in range(len(x)):
    if i == 0 :
        same.append(x[i])
    else:
        #這時的temp = ['款號','工序','員工編號']
        temp_x = str.split(x[i],'/')
        temp_y = str.split(x[i-1],'/')
        if temp_x[0] == temp_y[0]: #款號相同
            if temp_x[1] == temp_y[1]:
                same.append(x[i])
            else:
                prob += pulp.lpSum([num_vars[i] for i in same]) == 100*request[num][1]
                same = []
                same.append(x[i])
        else:
            prob += pulp.lpSum([num_vars[i] for i in same]) == 100*request[num][1]
            num = num + 1
            same = []
            same.append(x[i])

##限制式二：每個人工作秒數限制

person = []

for i in range(180):
    person.append([])
for i in range(len(x)):
    temp_x = str.split(x[i],'/') 
    time = stan[temp_x[0]+'/'+temp_x[1]]
    person[int(temp_x[2])].append(num_vars[x[i]]*time)
for i in person:
    if i != []:
        prob += 0 <= pulp.lpSum([i]) <= 36000
print(prob)

#求解
prob.solve()
#查看解
print("Status:", pulp.LpStatus[prob.status])

#查看解
for v in prob.variables():
    print(v.name, "=", v.varValue)
#type(prob.variables()) == list   
#將結果轉換成response格式
response = ""
for i in range(len(prob.variables())):
    if prob.variables()[i].varValue != 0:
        split = str.split(prob.variables()[i].name,"_")
        style_name = style_dict[split[1]]
        work_name = work_dict[style_name][split[1] + '/' + split[2]]
        person_name = name_list[int(split[3])]
        if i == 0:
            response = response + style_name + "/" + work_name + "," + person_name + "," + str(prob.variables()[i].varValue) 
        else:
            last_split = str.split(prob.variables()[i-1].name,"_")
            last_style = style_dict[last_split[1]]
            last_work = work_dict[last_style][last_split[1] + '/' +last_split[2]]
            if last_work == work_name:
                response = response + "," + person_name + "," + str(prob.variables()[i].varValue) 
            else:
                if last_style == style_name:
                    response = response + ";" + work_name + "," + person_name + "," + str(prob.variables()[i].varValue) 
                else:
                    response = response + '//' +style_name + "/" + work_name + "," + person_name + "," + str(prob.variables()[i].varValue) 
print(response)
