import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

kq = pd.read_csv('../education_data/3_kaoqin.csv')
chengji = pd.read_csv('../education_data/5_chengji.csv')
info = pd.read_csv('../education_data/2_student_info.csv')


def del_ht(s):
    if '\t' in s:
        return s[1:]
    else:
        return s


chengji['exam_numname'] = chengji['exam_numname'].apply(del_ht)
chengji.drop_duplicates(subset=['exam_numname', 'mes_sub_name', 'mes_StudentID'], keep='last', inplace=True)

###############################################################################################
# PART 1 成绩与考勤（曲线拟合）
###############################################################################################
# 1003 操场考勤机
# 99004 离校[移动考勤机]
# 99001 迟到[移动考勤机]
# 99005 进校[移动考勤机]
# 99002 校服[移动考勤机]
# 99003 早退[移动考勤机]
# 1001 迟到_晚到
# 1002 校徽_早退


def score_att():
    k1 = kq['bf_studentID'][
        (kq['ControllerID'] == 99001) |
        (kq['ControllerID'] == 99003) |
        (kq['ControllerID'] == 1001) |
        (kq['ControllerID'] == 1002)]

    # k2为学生异常考勤次数表
    k2 = pd.DataFrame(k1.value_counts()).reset_index().rename(index=str, columns={'bf_studentID': 'kq_times', 'index': 'mes_StudentID'})

    c1 = chengji[['mes_StudentID', 'mes_Z_Score']][chengji['mes_Z_Score'].isnull() == False]

    ck1 = pd.merge(c1, k2, how='inner', on='mes_StudentID')
    ck2 = ck1.groupby(['mes_StudentID', 'kq_times']).mean().reset_index()
    ck2.insert(0, '>0', 0)
    ck2.insert(0, '<0', 0)
    ck2.loc[ck2['mes_Z_Score'] > 0, '>0'] = 1
    ck2.loc[ck2['mes_Z_Score'] < 0, '<0'] = 1
    ck3 = ck2[['kq_times', '>0', '<0']].groupby('kq_times').sum().reset_index()
    ck3['per'] = ck3['>0'] / (ck3['>0'] + ck3['<0'])
    # ck3['per'] = ck3['<0'] / (ck3['>0'] + ck3['<0'])

    # 不同异常考勤次数的人群中，高于班级平均分的学生人数比例
    # scatter散点图
    plt.scatter(ck3['kq_times'], ck3['per'])
    plt.show()

    # 模型
    # 去除个别特殊点
    ck4 = ck3[ck3['per'] < 0.8]
    # ck4 = ck3[ck3['per'] > 0.2]

    x = ck4['kq_times'].values
    y = ck4['per'].values

    # 用二次多项式拟合
    coef2 = np.polyfit(x, y, 2)
    # 拟合函数
    poly_fit2 = np.poly1d(coef2)

    plt.plot(x, y, 's', label="nihe")
    plt.plot(x, poly_fit2(x), 'b', label="二阶拟合")
    plt.xlabel('迟到早退次数')
    plt.ylabel('优生比例')
    # plt.ylabel('差生比例')
    plt.show()

    # model_df = pd.concat([pd.Series(x), pd.Series(poly_fit2(x))], axis=1).rename(index=str, columns={0: 'kq_times', 1: 'model_value'})
    # # 输出
    # # ck2[['kq_times', 'mes_Z_Score']].to_json('./improve_kq_1.json', orient='split')
    # # ck3[['kq_times', 'per']].to_json('./improve_kq_2.json', orient='split')
    # # model_df[['kq_times', 'model_value']].to_json('./improve_kq_3.json', orient='split')


# score_att()
###############################################################################################
# PART 2 成绩稳定性（DBSCAN）
###############################################################################################


def stability():
    c1 = chengji[['exam_numname', 'mes_sub_name', 'mes_StudentID', 'mes_T_Score']][chengji['mes_T_Score'].isnull()==False]

    sub_name = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '技术']

    c5 = pd.DataFrame(data=None, columns=['mes_StudentID', 'mean', 'std'])
    c_heatmap = pd.DataFrame(data=None, columns=['mes_StudentID', 'sub', 'std'])
    for sub in sub_name:
        c2 = c1[['mes_StudentID', 'mes_T_Score']][c1['mes_sub_name'] == sub]
        c3 = c2['mes_StudentID'].value_counts().reset_index().rename(index=str, columns={'index': 'mes_StudentID', 'mes_StudentID': 'times'})
        c2 = pd.merge(c2, c3[c3['times'] > 10], how='right')[['mes_StudentID', 'mes_T_Score']]
        c_mean = c2.groupby('mes_StudentID').mean().reset_index().rename(index=str, columns={'mes_T_Score': 'mean'})
        c_std = c2.groupby('mes_StudentID').agg(np.std).reset_index().rename(index=str, columns={'mes_T_Score': 'std'})
        c4 = pd.merge(c_mean, c_std, how='inner')
        c5 = pd.concat([c5, c4])

        t = c4
        t.insert(1, 'sub', sub)
        c_heatmap = pd.concat([c_heatmap, t.drop(['mean'], axis=1)])

    # X = c5[['mean', 'std']].as_matrix()
    X = c5[['mean', 'std']].values

    # estimator = KMeans(n_clusters=2)
    # estimator.fit(X)
    # label_pred = estimator.labels_

    y_pred = DBSCAN(eps=1.19, min_samples=7.8).fit_predict(X)
    plt.scatter(X[:, 0], X[:, 1], c=y_pred)
    plt.xlabel('平均分')
    plt.ylabel('标准差')
    plt.show()

    dbscan = DBSCAN(eps=1.19, min_samples=7.8)
    dbscan.fit(X)
    label_pred = dbscan.labels_

    # 0: 稳定
    # 1: 不稳定
    # -1: 离群
    c6 = pd.concat([c5.reset_index().drop(['index'], axis=1), pd.Series(label_pred).rename('type')], axis=1)
    c_type = c6[['mes_StudentID', 'type']][c6['type']==1]
    c_info = info[['bf_StudentID', 'cla_Name']]
    c7 = pd.merge(c_info, c_type, how='inner', left_on='bf_StudentID', right_on='mes_StudentID')
    c8 = c7[['mes_StudentID']].drop_duplicates()
    c9 = pd.merge(c8, c_heatmap, how='left')
    c9.insert(0, 'y', -1)
    c9.loc[c9['sub'] == '语文', 'y'] = 0
    c9.loc[c9['sub'] == '数学', 'y'] = 1
    c9.loc[c9['sub'] == '英语', 'y'] = 2
    c9.loc[c9['sub'] == '物理', 'y'] = 3
    c9.loc[c9['sub'] == '化学', 'y'] = 4
    c9.loc[c9['sub'] == '生物', 'y'] = 5
    c9.loc[c9['sub'] == '政治', 'y'] = 6
    c9.loc[c9['sub'] == '历史', 'y'] = 7
    c9.loc[c9['sub'] == '地理', 'y'] = 8
    c9.loc[c9['sub'] == '技术', 'y'] = 9
    c10 = c9['mes_StudentID'].value_counts().reset_index().reset_index().drop(['mes_StudentID'], axis=1).rename(index=str, columns={'index': 'mes_StudentID', 'level_0': 'x'})
    c_res = pd.merge(c9, c10, how='inner')
    c_res = c_res[['x', 'y', 'mes_StudentID', 'sub', 'std']]
    # c_res.to_json('./stability.json', orient='split')
    print(c_res)

    # type = pd.Series(label_pred).value_counts().index
    # obj = {}
    # for i in type:
    #     x = X[label_pred == i]
    #     obj[i] = x.tolist()
    #     plt.scatter(x[:, 0], x[:, 1])
    # plt.show()
    #
    # json1 = json.dumps(obj, ensure_ascii=False, indent=2)
    # print(json1)
    # fl = open('./mean_std.json', 'w')
    # fl.write(json1)
    # fl.close()


# stability()
###############################################################################################
# PART 3 学科的线性相关程度
###############################################################################################
sub_name = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '技术']
sub_map = {
    '语文': 'yw_',
    '数学': 'sx_',
    '英语': 'yy_',
    '政治': 'zz_',
    '历史': 'ls_',
    '地理': 'dl_',
    '物理': 'wl_',
    '化学': 'hx_',
    '生物': 'sw_',
    '技术': 'js_',
}

obj = {}


def sub_relative(sub1, sub2):
    c1 = chengji[['exam_numname', 'mes_sub_name', 'mes_StudentID', 'mes_T_Score']][chengji['mes_T_Score'].isnull()==False]
    c2 = c1[(c1['mes_sub_name'] == sub1) | (c1['mes_sub_name'] == sub2)]
    c3 = c2.groupby(['mes_StudentID', 'mes_sub_name']).mean().reset_index()
    c4 = c3['mes_StudentID'].value_counts().reset_index().rename(index=str, columns={'index': 'mes_StudentID', 'mes_StudentID': 'times'})
    c5 = pd.merge(c3, c4[c4['times']==2], how='inner')
    x = c5['mes_T_Score'][c5['mes_sub_name']==sub1]
    y = c5['mes_T_Score'][c5['mes_sub_name']==sub2]

    # res = pd.concat([x.reset_index().drop(['index'], axis=1), y.reset_index().drop(['index'], axis=1)], axis=1)
    # obj[sub1 + '-' + sub2] = res.values.tolist()

    plt.scatter(x.values, y.values)
    plt.xlabel(sub1)
    plt.ylabel(sub2)

    coef = np.polyfit(x.values, y.values, 1)
    poly_fit = np.poly1d(coef)
    # print(min(x.values))
    # print(min(poly_fit(x.values)))
    # print(max(x.values))
    # print(max(poly_fit(x.values)))
    plt.plot(x.values, y.values)
    plt.plot(x.values, poly_fit(x.values))
    plt.show()

    t = {}

    model = LinearRegression()
    l = model.fit(x.values.reshape(-1, 1), y.values.reshape(-1, 1))

    plt.scatter(x.values, y.values)
    plt.scatter(x.values, y.values, c=l)
    plt.show()

    print('***')
    print(sub1, sub2)
    print(model.coef_)
    print(model.intercept_)
    t['k'] = model.coef_[0][0]
    t['b'] = model.intercept_[0]
    t['point'] = [100, 100*t['k']+t['b']]
    print(t)
    # print(model.predict(x.values.reshape(-1,1)))
    # print(model.score(x.values.reshape(-1,1), y.values.reshape(-1,1)))

# for i in range(10):
#     for j in range(i+1, 10):
#         sub_relative(sub_name[i], sub_name[j])


sub_relative('语文', '英语')
sub_relative('语文', '政治')
sub_relative('语文', '历史')
sub_relative('数学', '物理')
sub_relative('物理', '化学')
sub_relative('化学', '生物')
sub_relative('生物', '地理')
sub_relative('政治', '历史')
# json1 = json.dumps(obj,ensure_ascii=False,indent=2)
# print(json1)
# fl=open('./sub_relative.json', 'w')
# fl.write(json1)
# fl.close()
