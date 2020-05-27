# -*- coding:utf-8 -*-


# 学生ID-届数 表，以及顶尖毕业生历年成绩趋势分析
##############################################################################

import pandas as pd
import numpy as np

# 导入数据
data_cj = pd.read_csv('../edu_data/5_chengji.csv')
data_stu_info = pd.read_csv('../edu_data/2_student_info.csv')

# 1.对成绩表的处理

# 统一不同表之间相同列的名字
data_cj = data_cj.rename(columns={'mes_StudentID': 'bf_StudentID'})
#
data_cj = data_cj.fillna(0)
# 删除一些只在极个别考试中出现的分数项以及极个别届出现的考试（赋值为NaN）
data_cj[(data_cj['mes_Score'] < 0) | (data_cj['mes_sub_name'] == '1B模块总分') | (data_cj['exam_numname'] == '2018-2019新高一7月测试')] = np.nan
# '1B模块总分'只在2016届的高三模拟、联考中出现过
# 只有一届学生有新高一测试：'2018-2019新高一7月测试'

# 在原表删除所有NaN所在行
data_cj.dropna(axis=0, how='any', inplace=True)

# 2.对学生信息表的处理
data_stu_info = data_stu_info[['bf_StudentID', 'cla_Name']]


##############################################################################
# Step 1 得到学生ID-届数表

# func 将高x和xx级进行转换，并将届保存为period


def func_class(m, i):
    n = data_stu_info[['cla_Name', 'bf_StudentID']][
        (data_stu_info.cla_Name.str.contains(m)) & ~(data_stu_info.cla_Name.str.contains('IB'))
        & ~(data_stu_info.cla_Name.str.contains('未分班'))]
    n['period'] = i
    return n


# 得到学生ID-届数表 stu_class
# func只能判断出班级名称中带有高一高二高三的学生的届数
stu_class = pd.concat([func_class('高三', 16), func_class('高二', 17), func_class('高一', 18)])
stu_class = stu_class[['bf_StudentID', 'period']]

# 获得ID，届数，考试名称，考试学期表data_piece（data_piece只有部分学生的届数判断出来了）
# 获得merge合并后perid为NaN的表perid_nan（即func无法判断届数的学生）

data_cj1 = data_cj[['exam_numname', 'bf_StudentID', 'exam_term']]
data_class = pd.merge(stu_class, data_cj1, on='bf_StudentID', how='right')
data_piece = data_class.dropna(axis=0, how='any', inplace=False)
perid_nan = data_class[data_class.period != data_class.period]
# 判断出1561名学生的届数，仍有2300名学生未判断出


# 获得perid_nan中考试名称不包含 特定可以判断为高三的字眼 的学生，表s
s = perid_nan[['exam_numname', 'bf_StudentID', 'exam_term']][
    ~(perid_nan.exam_numname.str.contains('高三')) & ~(perid_nan.exam_numname.str.contains('五校联考')) &
    ~(perid_nan.exam_numname.str.contains('十校联考'))]
s['period'] = np.nan

# func2 考试名字中带有特定字眼判断为高三，届数为其考试学期的34位-2


def func2_class(m):
    n = perid_nan[['exam_numname', 'bf_StudentID', 'exam_term']][
        ((perid_nan.exam_numname.str.contains('高三')) | (perid_nan.exam_numname.str.contains('五校联考')) |
         (perid_nan.exam_numname.str.contains('十校联考'))) & (perid_nan.exam_term.str.contains(m))]
    n['period'] = int(m[2:4])-2
    return n


# 获得通过func2判断出的ID，届数，考试名称，考试学期表，并与data_piece连接得到data_class_test
data_class_test = pd.concat([data_piece, func2_class('2013-2014'), func2_class('2014-2015'), func2_class('2015-2016'), func2_class('2016-2017'), func2_class('2017-2018'),
                             func2_class('2018-2019'), s], sort=False)
# print(data_class_test)


# 判断出3771名学生的届数，学生总数为3861，有90名学生未能判断出来
stuid_class = data_class_test.dropna(axis=0, how='any', inplace=False)
stuid_class = stuid_class[['bf_StudentID', 'period']].groupby(by='bf_StudentID').mean().reset_index()
# print('*****学生ID对应级（入学年份）表*****')
# print(stuid_class)

data_cj2 = data_cj[['exam_numname', 'bf_StudentID', 'exam_term', 'mes_Score', 'mes_sub_name']][
    (~(data_cj.exam_numname.str.contains('考察'))) & (~(data_cj.exam_numname.str.contains('考查')))]
data_cj2 = pd.merge(data_cj2, stuid_class, on='bf_StudentID')
# *****学生ID、届数、考试名称、考试学期、考试分数 表（不包含考查课）*****
# print(data_cj2)


##############################################################################
# Step 2 各届高三学生最后一次考试成绩top30

# 各届高三下学习成绩（16级没有下半学期考试数据）
data_cj4 = data_cj2[['exam_numname', 'bf_StudentID', 'period', 'exam_term', 'mes_Score', 'mes_sub_name']][
    ((data_cj2.period == 11) & (data_cj2.exam_term.str.contains('2013-2014-2'))) |
    ((data_cj2.period == 12) & (data_cj2.exam_term.str.contains('2014-2015-2'))) |
    ((data_cj2.period == 13) & (data_cj2.exam_term.str.contains('2015-2016-2'))) |
    ((data_cj2.period == 14) & (data_cj2.exam_term.str.contains('2016-2017-2'))) |
    ((data_cj2.period == 15) & (data_cj2.exam_term.str.contains('2017-2018-2'))) |
    ((data_cj2.period == 16) & (data_cj2.exam_term.str.contains('2018-2019-1')))
    ]
# print(data_cj4)

# 每届高三最后一次考试(maybe)
data_cj4 = data_cj4[['exam_numname', 'bf_StudentID', 'period', 'mes_Score', 'mes_sub_name']][
    (data_cj4.exam_numname == '2013-2014第二次五校联考') | (data_cj4.exam_numname == '2015年高三第二次五校联考') |
    (data_cj4.exam_numname == '2016届高三第二次五校联考') | (data_cj4.exam_numname == '2017年5月高三“五校联考”') |
    (data_cj4.exam_numname == '2017学年第二学期高三五校联考') | (data_cj4.exam_numname == '2018学年第一学期高三五校联考')
    ]
data_cj4 = data_cj4.groupby(['period', 'bf_StudentID']).sum().reset_index()


def func_top(i):
    a = data_cj4[data_cj4['period'] == i].sort_values(by='mes_Score', ascending=False).head(30)
    print('**************%d级总分第1名*************' % i)
    print(a.head(1))
    print('**************%d级总分第30名************' % i)
    print(a.tail(1))
    return a

# func_scale 由于14、15、16级高三考试的总分为450，而11、12、13级为750，将分数进行按比例计算，方便查看出成绩变化


def func_scale(i):
    a = data_cj4[data_cj4['period'] == i].sort_values(by='mes_Score', ascending=False).head(30)
    a['mes_Score'] = a['mes_Score'].map(lambda x: x*750/450).round(1)
    print('**************%d级总分第1名*************' % i)
    print(a.head(1))
    print('**************%d级总分第30名************' % i)
    print(a.tail(1))
    return a


# 14、15级的高三考试只有语数外三门；16级的高三考试（上学期）没有语文数学
data_cj4 = pd.concat([func_top(11), func_top(12), func_top(13), func_scale(14), func_scale(15), func_scale(16)], sort=False)
print('*****每一级学生高三某次考试总分前30*****')
print(data_cj4)


"""
**************11级总分第1名*************
     period  bf_StudentID  mes_Score
187    11.0       11044.0      667.0
**************11级总分第30名************
     period  bf_StudentID  mes_Score
390    11.0       11280.0      607.5
**************12级总分第1名*************
     period  bf_StudentID  mes_Score
836    12.0       11752.0      632.0
**************12级总分第30名************
     period  bf_StudentID  mes_Score
884    12.0       11803.0      590.0
**************13级总分第1名*************
      period  bf_StudentID  mes_Score
1043    13.0       12040.0      647.0
**************13级总分第30名************
      period  bf_StudentID  mes_Score
1062    13.0       12064.0      596.0
**************14级总分第1名*************
      period  bf_StudentID  mes_Score
1300    14.0       12432.0      625.0
**************14级总分第30名************
      period  bf_StudentID  mes_Score
1622    14.0       12781.0      583.3
**************15级总分第1名*************
      period  bf_StudentID  mes_Score
1851    15.0       13620.0      643.3
**************15级总分第30名************
      period  bf_StudentID  mes_Score
1934    15.0       13714.0      605.0
**************16级总分第1名*************
      period  bf_StudentID  mes_Score
2176    16.0       13975.0      635.0
**************16级总分第30名************
      period  bf_StudentID  mes_Score
2259    16.0       14065.0      590.0
"""

# ***************************************************************************************************
# cj5 = cj[['exam_numname', 'bf_StudentID', 'exam_term', 'mes_Score', 'mes_sub_name']][
#     cj.exam_numname.str.contains('期末考试')
# ]
# # 2018-2019-1期末考试没有录入考试科目信息，只有分数
# cj5_1 = cj5[['exam_numname', 'exam_term', 'bf_StudentID', 'mes_Score']]\
#     .groupby(['exam_term', 'exam_numname', 'bf_StudentID']).sum()
# # 每学期的期末考试 每个人的总分情况
# # print(cj5_1)
# cj5_2 = cj5[['exam_numname', 'exam_term', 'bf_StudentID', 'mes_Score', 'mes_sub_name']] \
#     .groupby(['exam_term', 'exam_numname', 'bf_StudentID', 'mes_sub_name']).sum()
# # 每学期的期末考试 每个人的单科情况
# print(cj5_2)

# ***************************************************************************************************


# def func3(df):
#     df['grade'] = int(df['exam_term'][2:4]) - df['period'] + 1
#     return df
#
#
# gra = cj2.apply(func3, axis=1)
# # print(gra)
# # 有180条数据记录是学生参加了入学以前的考试（数据总数为231248）
# gra = gra[(gra.grade <= 3) & (gra.grade >= 1)]
# gra = gra[['grade', 'period', 'mes_T_Score', 'mes_sub_name']].groupby(['period', 'grade', 'mes_sub_name']).describe()
# # *****某级学生在某一年级时的各科成绩 表*****
# # print(gra)


# # *******************************************************************************************
# cj3 = cj[['exam_numname', 'bf_StudentID', 'exam_term', 'mes_T_Score', 'mes_sub_name']][
#     (cj.exam_numname.str.contains('考察')) | (cj.exam_numname.str.contains('考查')) |
#     (cj.mes_sub_name.str.contains('技术'))]
# cj3 = cj3[['bf_StudentID', 'exam_term', 'mes_sub_name', 'mes_T_Score']]
# cj3 = pd.merge(cj3, r, on='bf_StudentID')
# # *****考查课以及技术课*****
# # print(set(cj3['mes_sub_name']))
# # print(cj3.describe())
#
#
# def func4(df):
#     df['grade'] = int(df['exam_term'][2:4]) - df['period'] + 1
#     return df
#
#
# gre = cj3.apply(func4, axis=1)
# # print(gra)
# # 有180条数据记录是学生参加了入学以前的考试（数据总数为231248）
# gre = gre[(gre.grade <= 3) & (gre.grade >= 1)]
# # gre = gre[['mes_T_Score', 'mes_sub_name', 'period', 'grade']].groupby(['period', 'mes_sub_name',  'grade']).mean()
# gre_c = gre[(gre['grade'] == 3) & ((gre['mes_sub_name'] == '技术') | (gre['mes_sub_name'] == '体育'))]
# gre_c2 = gre[(gre['grade'] == 2) & ((gre['mes_sub_name'] == '技术') | (gre['mes_sub_name'] == '体育'))]
# print(set(gre_c['period']))
# print(set(gre_c2['period']))
# # *****音乐和美术数据不足，高三只有{13.0, 14.0, 15.0}有且15只有一人，高二只有{16.0, 14.0}且14只有一人*****
