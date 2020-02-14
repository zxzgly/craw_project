# encoding:utf-8
# FileName: send_email
# Author:   xiaoyi | 小一
# email:    1010490079@qq.com
# Date:     2020/2/14 11:54
# Description: 发送邮件
import smtplib
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_email_content(df_data_1, df_data_2):
    """
    生成邮件正文内容
    @param df_data_1:
    @param df_data_2:
    @return:
    """
    content = """
    <strong>创作者：小一</strong><br>
    代码获取及讲解：请关注公众号【知秋小梦】<br><br>
    <strong>功能：</strong><br>
    1、每日定时爬取疫情数据，绘制成热力地图<br>
    2、针对疫情数据，和前一日进行数据对比<br>
    3、将 ①、②的结果通过 邮件发送到列表<br><br>
    数据每日更新时间：08:38<br>
    数据来源：https://ncov.dxy.cn/ncovh5/view/pneumonia <br><br>
    <strong>本程序仅供学习交流，请勿用于非法用途<br>
    欢迎关注公众号【知秋小梦】加群学习交流<br>
    疫情时期，大家保护好自己</strong><br><br><br>
    """
    content += generate_html(df_data_2, '各省份较前一日新增人数', 'picture')
    content += generate_html(df_data_1, '各城市较前一日新增人数', 'none')

    return content


def generate_html(df_data, title, tag='picture'):
    """
    生成html
    @param df_data:
    @param title:
    @param tag:
    @return:
    """
    df_html = df_data.to_html(index=True)
    """修改html样式"""
    if tag == 'picture':
        html = str(df_html).replace(
            '<table border="1" class="dataframe">',
            '<p><img src="cid:image1" alt="最新数据地图" width="1200" height="600"></a></p>'
            '<p><img src="cid:image2" alt="最新数据地图" width="1200" height="600"></a></p>'
            '<table border="0" class="dataframe" style="width:100%" cellspacing="2" cellpadding="2">'
        )
    else:
        html = str(df_html).replace(
            '<table border="1" class="dataframe">',
            '<table border="0" class="dataframe" style="width:100%" cellspacing="2" cellpadding="2">'
        )

    html = str(html).replace(
        '<tr style="text-align: right;">',
        '<div style="text-align:center;width:100%;padding: 8px; line-height: 1.42857; vertical-align: top; '
        'border-top-width: 1px; border-top-color: rgb(221, 221, 221); background-color: #3399CC;color:#fff">'
        '<strong>''<font size="4">' + title + '</font>''</strong></div>'
        '<tr style="background-color:#FFCC99;text-align:center;">'
     )
    html = str(html).replace('<tr>', '<tr style="text-align:center">')
    html = str(html).replace('<th></th>', '<th>num</th>')

    style = """
    <style type="text/css">
    table {
    border-right: 1px solid #99CCFF;
    border-bottom: 1px solid #99CCFF;
    }
    table td {
    border-left: 1px solid #99CCFF;
    border-top: 1px solid #99CCFF;
    }
    table th {
    border-left: 1px solid #99CCFF;
    border-top: 1px solid #99CCFF;
    }
    </style>
    """

    return style+html


def send_email(date_str, img_path_list, df_data_1, df_data_2):
    """
    发送电子邮件
    @param date_str:
    @param img_path_list:
    @param df_data_1:
    @param df_data_2:
    @return:
    """
    # 设置发送人
    sender = 'zhiqiuxiaoyi@qq.com'
    # 设置接收人
    receiver_list = ['reveiver_1@qq.com', 'reveiver_2@qq.com']

    # 设置主题
    subject = '截止 ' + date_str + ' 疫情最新数据（自动推送）'
    # 设置发送内容:1：发送html表格数据
    message = MIMEMultipart()
    emain_content = get_email_content(df_data_1, df_data_2)
    send_text = MIMEText(emain_content, 'html', 'utf-8')
    message.attach(send_text)

    # 读取图片并创建MIMEImage
    for i, imag_filepath in enumerate(img_path_list):
        with open(imag_filepath, 'rb') as fp:
            msg_image = fp.read()
        msg_image = MIMEImage(msg_image)
        # 定义图片 ID，在 HTML 文本中引用
        msg_image.add_header('Content-ID', '<image{0}>'.format(i + 1))
        message.attach(msg_image)

    # 设置一些附属表头参数
    message['From'] = sender
    message['To'] = ','.join(receiver_list)  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
    message['Subject'] = Header(subject, 'utf-8')
    # 登陆邮箱发送
    username = 'zhiqiuxiaoyi@qq.com'
    # qq授权码(此处需要填写qq授权码)
    password = 'xxxxxxxxx'

    """加密传送"""
    smtp_server = 'smtp.qq.com'
    smtp_port = 587
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()

    # 登陆并发送
    smtp.login(username, password)
    smtp.sendmail(sender, message['To'].split(','), message.as_string())
    smtp.quit()

    print(u'发送电子邮件完成，已成功发送至列表')


if __name__ == '__main__':
    pass