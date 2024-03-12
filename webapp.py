#!/usr/bin/python3

import io
import cgi
import sys
import pymysql.cursors
import http.cookies
import uuid
import os

# cgiプログラムの出力漢字コード設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 入力フォームを受け取るオブジェクト
form = cgi.FieldStorage()

# エラーチェック関連フラグ
op_selected = True
able_to_login = True
able_to_register = True

# URLパラメータ読み出し : name と number と text
if 'name' not in form:
    name = None
else:
    name = form['name'].value
if 'number' not in form:
    number = None
else:
    number = form['number'].value
if 'text' not in form:
    text = None
else:
    text = form['text'].value

# データベースアクセス用オブジェクト作成
conn = pymysql.connect(host='localhost', user='class', db='rdbtest',
                       charset='utf8', cursorclass=pymysql.cursors.DictCursor)
cu = conn.cursor()

# 書き込みがクリックされる
if form.getfirst('write') != None:
    # CookieからセッションIDを取得
    cookie_string = os.environ.get('HTTP_COOKIE')
    cookie = http.cookies.SimpleCookie()
    cookie.load(str(cookie_string))
    if 'session_id' not in cookie:
        cookie['session_id'] = None
    sql = f"select * from LOGIN_C221034 where session_id='{cookie['session_id'].value}';"
    cu.execute(sql)
    result = cu.fetchall()
    # URLパラメータが存在するならばデータベースに書き込み
    if name != None and number != None and text != None and len(result) == 1:
        sql = 'insert C221034 values ('+str(number) + \
            ', "'+str(name)+'", "'+text+'", "'+str(result[0]["userid"])+'");'
        cu.execute(sql)
        conn.commit()

# 削除がクリックされる
if form.getfirst('del') != None:
    # 削除オプションの選択がない場合
    if form.getfirst('op') == None:
        op_selected = False
        pass

    # 削除オプションが選択された場合
    elif form["op"].value == "1" and number != None:
        sql = 'delete from C221034 where number='+str(number) + ';'
        cu.execute(sql)
    elif form["op"].value == "2" and name != None:
        sql = 'delete from C221034 where name="'+str(name)+'";'
        cu.execute(sql)
    elif form["op"].value == "3" and name != None and number != None:
        sql = 'delete from C221034 where number='+str(number) + \
            ' and name="'+str(name)+'";'
        cu.execute(sql)
    elif name != None and number != None and text != None:
        sql = 'delete from C221034 where number='+str(number) + \
            ' and name="'+str(name)+'" and text= "'+text+'";'
        cu.execute(sql)
    conn.commit()

# ログアウト処理
if form.getfirst('logout') != None:
    cookie_string = os.environ.get('HTTP_COOKIE')
    cookie = http.cookies.SimpleCookie()
    cookie.load(str(cookie_string))
    if 'session_id' not in cookie:
        cookie['session_id'] = None
    sql = f"UPDATE LOGIN_C221034 SET session_id = 'NO DATA' where session_id='{cookie['session_id'].value}';"
    cu.execute(sql)
    conn.commit()


# ログイン処理
first_login = False

if form.getfirst('login') != None:
    # ユーザーIDとパスワードが一致の確認
    sql = f"select * from LOGIN_C221034 where userid='{form.getfirst('userid')}' and password='{form.getfirst('password')}';"
    cu.execute(sql)
    result = cu.fetchall()

    # if form.getfirst('userid') == result[0]['userid'] and form.getfirst('password') == result[0]['password']:
    # 一致していれば
    if len(result) == 1:
        # セッションIDを生成
        session_id = str(uuid.uuid4())
        # クッキーに保存
        print("Set-Cookie: session_id=" + session_id)
        # データベースに保存
        sql = f"UPDATE LOGIN_C221034 SET session_id = '{session_id}' where userid='{form.getfirst('userid')}'; "
        cu.execute(sql)
        conn.commit()

        # 初回ログイン用のフラグ
        first_login = True
    else:
        able_to_login = False
# アカウント登録処理
elif form.getfirst('register') != None:
    # ユーザーIDの重複をチェック
    sql = f"select * from LOGIN_C221034 where userid='{form.getfirst('userid')}';"
    cu.execute(sql)
    result = cu.fetchall()

    # 重複していれば
    if len(result) == 1:
        able_to_register = False
        pass
    # 重複していなければ登録処理
    else:
        sql = f"insert LOGIN_C221034 values ('{form.getfirst('userid')}', '{form.getfirst('password')}', 'NO DATA')"
        cu.execute(sql)
        conn.commit()

# CookieからセッションIDを取得
cookie_string = os.environ.get('HTTP_COOKIE')
cookie = http.cookies.SimpleCookie()
cookie.load(str(cookie_string))

if 'session_id' not in cookie:
    cookie['session_id'] = None
if cookie['session_id'].value == 'NO DATA':
    cookie['session_id'] = None
# Cookieに保存されているセッションIDがデータベースと一致するか
sql = f"select * from LOGIN_C221034 where session_id='{cookie['session_id'].value}';"
cu.execute(sql)
result = cu.fetchall()

# セッションIDが一致した場合
if len(result) == 1 or first_login:
    # データベースから全レコード取り出し
    sql = "select * from C221034;"
    cu.execute(sql)
    result = cu.fetchall()

    # 一連の操作が終わったら close する
    conn.close()

    # 表示セクション
    print("Content-type: text/html\n")
    print("<html><head>")
    print("<meta charset=\"utf-8\"/>")
    print("</head><body>")

    print("<pre>")
    # 得られた結果は１タプルごとのリストであり，１タプルは１つの辞書型となる
    if result != None:
        print(result)
    print("</pre>")
    # 表で表示する
    print("タプル一覧:")
    print("<table border=1>")
    print("<tr><th>number</th><th>name</th><th>text</th><th>editor</th></tr>")
    for i in range(len(result)):
        # fetchall() で result に獲得した値は result[i]['属性名'] で得られる
        print("<tr><td>")
        print(result[i]['number'])
        print("</td><td>")
        print(result[i]['name'])
        print("</td><td>")
        print(result[i]['text'])
        print("</td><td>")
        print(result[i]['editor'])
        print("</td></tr>")
    print("</table>")
    # フォームの表示
    print('<form action="/cgi-bin/webappC221034.txt" method="post">')
    print('<p><label>番号 : ')
    print('<input type=number name=number min=0>')
    print('</label>')
    print('<p><label>名前 : ')
    print('<input type=text name=name size=64 maxlength=256>')
    print('</label>')
    print('<p><label>本文 : ')
    print('<input type=text name=text size=128 maxlength=512>')
    print('</label>')
    print('<p><input type=submit name=write value="書き込み">')
    print('<p><input type=submit name=del value="削除">')
    print('''
        <select name="op">
        <option value="">--削除のオプションを選択してください--</option>
        <option value="1">番号が一致</option>
        <option value="2">名前が一致</option>
        <option value="3">番号と名前が一致</option>
        <option value="4">すべての属性が一致</option>
        </select>''')
    print('<p><br><input type=submit name=logout value="ログアウト">')
    print('</form>')

    # プルダウンを削除時選択してなかった場合
    if op_selected == False:
        print("<script>alert('削除のオプションが選択されていません')</script>")

    print("</body></html>")

else:
    print("Content-type: text/html\n")
    print("<html><head>")
    print("<meta charset=\"utf-8\"/>")
    print("</head><body>")
    print('''
        <h1>ログイン画面</h1>
        <form action="/cgi-bin/webappC221034.txt" method="post">
            <label for="userid">ユーザーID:</label>
            <input type="text" name="userid" required>
            <br>
            <label for="password">パスワード:</label>
            <input type="password" name="password" required>
            <br>
            <input type="submit" name="login" value="ログイン">
            <input type="submit" name="register" value="登録">
        </form>
        ''')

    # エラー表示
    if able_to_login == False:
        print("<p><font color='red'>ユーザーIDまたはパスワードが違います。</font></p>")
    elif able_to_register == False:
        print("<p><font color='red'>このユーザーIDはすでに使われています。</font></p>")

    print("""<p>説明<br>
          ログインするためには以下に表示されているIDとパスワードを入力してください。<br>
          入力後ログインボタンを押すとログインできます。<br>
          登録ボタンを押すと入力したIDとパスワードで新たにユーザーを登録します。<br>
          ただし、同じuseridを用いて登録はできません</p>""")
    print('<a href="https://ml.cse.oka-pu.ac.jp/cgi-bin/tableC221034.txt">テーブルリセット</a>')

    print("""<p>※ログイン状態の維持のためにCookieを用いています。</p>""")
    # パスワード一覧表示
    sql = f"select * from LOGIN_C221034;"
    cu.execute(sql)
    result = cu.fetchall()
    print("<p>IDとパスワード一覧<br>")
    print("<table border=1>")
    print("<tr><th>userid</th><th>password</th><th>session_id</th></tr>")
    for i in range(len(result)):
        print("<tr><td>")
        print(result[i]['userid'])
        print("</td><td>")
        print(result[i]['password'])
        print("</td><td>")
        print(result[i]['session_id'])
        print("</td></tr>")
    print("</table>")

    print("</body></html>")
    conn.close()
