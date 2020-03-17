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
