# -*- coding:utf-8 -*-


# Part1：统计学校范围内学生的基本情况
##############################################################################

import pandas as pd
# 显示所有列
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)

# 数据加载
data_origin = pd.read_csv('../education_data/2_student_info.csv')

# 数据探索
print(data_origin.info())
print(data_origin.describe())
print(data_origin.head())
print(data_origin.tail())

'''
RangeIndex: 1765 entries, 0 to 1764
Data columns (total 14 columns):
bf_StudentID        1765 non-null int64
bf_Name             1765 non-null object
bf_sex              1765 non-null object
bf_nation           1765 non-null object
bf_BornDate         1682 non-null float64
cla_Name            1765 non-null object
bf_NativePlace      1640 non-null object
Bf_ResidenceType    1765 non-null object
bf_policy           1765 non-null object
cla_id              1765 non-null int64
cla_term            1765 non-null object
bf_zhusu            708 non-null float64
bf_leaveSchool      26 non-null object
bf_qinshihao        708 non-null float64
'''

##############################################################################
# 性别

# 由describe可知，bf_sex无缺失值，总人数1765
sex_null = 0
print('性别的缺失值数为', sex_null)
print('\b')

num_all = 1765
print('学生的总人数为', num_all)
print('\b')

# 统计男女生的人数
data_origin['bf_sex'] = data_origin['bf_sex'].map({'男': 1, '女': 0})
num_male = sum(data_origin['bf_sex'])
num_female = num_all - num_male
print('男生的数量为', num_male, '女生的数量为', num_female)
print('\b')
# 男性人数为943人，女性人数为822人

##############################################################################
# 民族

# bf_nation无缺失值
nation_null = 0
print('学生民族数据缺失数为', nation_null)
print('\b')

print(data_origin['bf_nation'].value_counts())
print('\b')

'''
汉族      1750
满族         4
 土家族       3
苗族         3
朝鲜族        2
回族         2
畲族         1
'''
# 该部分建议使用饼状图反映，点击可展示具体少数民族人数

##############################################################################
# 出生地分布

# Step1：统计缺失值并剔除
NativePlace_null = num_all - 1640
# NativePlace_null = len(data_origin['bf_NativePlace'][pd.isnull(data_origin['bf_NativePlace'])])
print('出生地缺失的数为', NativePlace_null)
print('\b')
# 出生地缺失的数据有125人

# 将学生出生地缺失的行删除
data_NativePlace = data_origin.drop(data_origin[data_origin['bf_NativePlace'].isnull()].index)
print('剔除出生地缺失的行后数据量为', data_NativePlace.shape[0])
print('\b')
# 剩下的行数为1640行

# print(set(data_NativePlace['bf_NativePlace']))
# 将学生出生地中错误数据进行删除，如汉、汉族、中国
data_NativePlace = data_NativePlace.drop(data_NativePlace[data_NativePlace['bf_NativePlace'] == '汉族'].index)
data_NativePlace = data_NativePlace.drop(data_NativePlace[data_NativePlace['bf_NativePlace'] == '汉'].index)
data_NativePlace = data_NativePlace.drop(data_NativePlace[data_NativePlace['bf_NativePlace'] == '中国'].index)
print('去除错误数据后的数据量为', data_NativePlace.shape[0])
print('\b')
# 剩下的行数为1610行

# Step2:删除构建主要省级城市
# 构建主要的省级城市  34个
Province = ["北京", "上海", "天津", "重庆", "河北", "山西", "辽宁", "吉林", "河南", "江苏", "浙江", "安徽", "福建",
            "江西", "山东", "湖北", "湖南", "广东", "海南", "四川", "贵州", "云南", "陕西", "甘肃", "青海", "黑龙江",
            "内蒙古", "广西", "西藏", "宁夏", "新疆", "台湾", "香港", "澳门"]

# 通过循环来统计数目
num_city = [0]*34
for i in range(0, 34):
    data_NativePlace_new = data_NativePlace[data_NativePlace['bf_NativePlace'].str.contains(Province[i])]
    num_city[i] = data_NativePlace_new.shape[0]
    print("城市", Province[i], "的数量为", num_city[i])
print('\b')

# 通过循环来去除主要省市，得到出生地字段不是主要省级城市的表
for j in range(0, 34):
    data_NativePlace = data_NativePlace.drop(data_NativePlace[data_NativePlace['bf_NativePlace'].str.contains(Province[j])].index)
# print(data_NativePlace)

# 处理浙江的城市（有些浙江城市未写浙江，只写了城市名）(获得浙江内各城市人数，且得到出生字段也不是浙江城市的表）

Zhejiang = ["宁波", "慈溪", "岱山", "东阳", "奉化", "富阳", "海曙", "杭州", "黄岩", "嘉善", "嘉兴", "建德", "江北", "乐清",
            "宁海", "浦江", "衢州", "三门", "上虞", "绍兴", "嵊州", "台州", "桐庐", "温州", "咸祥", "象山", "新昌", "义乌",
            "鄞州", "余姚", "浙甬", "舟山", "诸暨", "丽水"]

sum_zhejiang = 0
num_zhejiang = [0]*(len(Zhejiang))
for i in range(0, len(Zhejiang)):
    data_NativePlace_new = data_NativePlace[data_NativePlace['bf_NativePlace'].str.contains(Zhejiang[i])]
    num_zhejiang[i] = data_NativePlace_new.shape[0]
    print('属于浙江', Zhejiang[i], '的人数有', num_zhejiang[i])
    data_NativePlace = data_NativePlace.drop(data_NativePlace[data_NativePlace['bf_NativePlace'].str.contains(Zhejiang[i])].index)
print(num_zhejiang)
print('\b')

for i in range(0, len(Zhejiang)):
    sum_zhejiang += num_zhejiang[i]

# num_city[10] 是出生地写了浙江的，sum_zhejiang是没有写浙江，但写了浙江但城市名的
num_city[10] = num_city[10] + sum_zhejiang
print("属于浙江的其他的城市有", sum_zhejiang, "个")
print("属于浙江省一共有", num_city[10], "名学生")
print('\b')

# 修改其他的省市
# 打印剩余的
# print(data_NativePlace)
# print('\b')

# 查看得知剩余四条特殊数据，处理并入
# 安徽合肥、皖
num_city[11] = num_city[11] + 2
# 江西吉安
num_city[13] = num_city[13] + 1
# 辽宁鞍山
num_city[6] = num_city[6] + 1

# 打印各个省市的分布情况
for i in range(0, len(Province)):
    print("来自", Province[i], "的有", num_city[i], "位学生")
print('\b')

# 打印各个省市人数非0的分布情况
for i in range(0, len(Province)):
    if num_city[i] != 0:
        print("来自", Province[i], "的有", num_city[i], "位学生")
print('\b')

##############################################################################
# 学生政治面貌统计

# 学生政治面貌的缺失值0
num_policy_null = 0
print(num_policy_null)
print('\b')

# 缺失值数量为0

# 统计学校内学生的政治面貌，分为：共青团员，少先队员，一般

policy = ["共产党党员", "共青团员", "少先队员", "一般", "民主党派"]
num_policy = [0]*5

for i in range(5):
    data_policy_new = data_origin[data_origin['bf_policy'].str.contains(policy[i])]
    num_policy[i] = data_policy_new.shape[0]
for i in range(5):
    print('政治面貌为', policy[i], '的人数为', num_policy[i])

print('\b')

# 共产党党员1人，共青团员1662人，少先队员23人，一般为78人，民主党派1人

##############################################################################
# 学生年龄统计

# 统计学生年龄缺失值
num_age_null = len(data_origin['bf_BornDate'][pd.isnull(data_origin['bf_BornDate'])])
print("学生年龄缺失数量为", num_age_null)
print('\b')

# 缺失人数为83人，删除缺失的学生记录
data_age = data_origin.drop(data_origin[pd.isnull(data_origin['bf_BornDate'])].index)

# 计算学生的年级，如果都是以2019开始计算
data_age['bf_BornDate'] = 2019 - data_age['bf_BornDate']

# 统计学生的年龄分布情况
num_age_15 = len(data_age['bf_BornDate'][data_age['bf_BornDate'] <= 15])
num_age_16 = len(data_age['bf_BornDate'][data_age['bf_BornDate'] == 16])
num_age_17 = len(data_age['bf_BornDate'][data_age['bf_BornDate'] == 17])
num_age_18 = len(data_age['bf_BornDate'][data_age['bf_BornDate'] == 18])
num_age_19 = len(data_age['bf_BornDate'][data_age['bf_BornDate'] == 19])
num_age_20 = len(data_age['bf_BornDate'][data_age['bf_BornDate'] >= 20])

print("小于等于15岁的学生数有", num_age_15, "人", "年龄最小的岁数为", min(data_age['bf_BornDate']), "岁")
print("16岁的学生数有", num_age_16, "人")
print("17岁的学生数有", num_age_17, "人")
print("18岁的学生数有", num_age_18, "人")
print("19岁的学生数有", num_age_19, "人")
print("大于等于20岁的学生数有", num_age_20, "人", "年龄最大的岁数为", max(data_age['bf_BornDate']), "岁")
print('\b')

##############################################################################
# 住校学生统计

# 统计学生住校信息栏为空的数据，表示学生住外面
num_zhusu_null = len(data_origin['bf_zhusu'][pd.isnull(data_origin['bf_zhusu'])])

print("住校学生有", (data_origin.shape[0] - num_zhusu_null), "住校外的学生有", num_zhusu_null)
print('\b')

# 统计各个年龄段的男女比例


def statistic_age_sex(age):
    count = [0, 0]
    sex = [1, 0]
    for i in range(len(count)):
        for j in range(data_age.shape[0]):
            if (data_age['bf_BornDate'].iloc[j] == age) and (data_age['bf_sex'].iloc[j] == sex[i]):
                count[i] += 1
    print("年龄为", age, "的男生数有", count[0], "年龄为", age, "的女生数有", count[1])


statistic_age_sex(15)
statistic_age_sex(16)
statistic_age_sex(17)
statistic_age_sex(18)
statistic_age_sex(19)
statistic_age_sex(20)


'''
年龄为 15 的男生数有 2 年龄为 15 的女生数有 5
年龄为 16 的男生数有 254 年龄为 16 的女生数有 174
年龄为 17 的男生数有 313 年龄为 17 的女生数有 253
年龄为 18 的男生数有 232 年龄为 18 的女生数有 241
年龄为 19 的男生数有 96 年龄为 19 的女生数有 111
年龄为 20 的男生数有 0 年龄为 20 的女生数有 1
'''
