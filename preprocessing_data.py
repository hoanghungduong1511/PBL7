import pandas as pd
import pymysql

# Đọc file Excel
df = pd.read_excel('Data_train_04_05.xlsx', engine='openpyxl')

# Chuẩn hoá dữ liệu
df['create_at'] = pd.to_datetime(df['created_at']).dt.date
df['experience'] = df['experience'].fillna(0)

# Kết nối MySQL
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='pbl7',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()

# Duyệt và chèn từng dòng vào bảng base
for _, row in df.iterrows():
    sql = """
        INSERT INTO base (
            job_title, company_name, job_type,
            location, salary, experience, create_at,
            id_hr, industry
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        row['title'],
        row['company_name'],
        'offline',  # hoặc đọc từ file nếu có
        row['location'],
        row['salary'],
        row['experience'],
        row['create_at'],
        None,  # id_hr chưa có nên để None
        row['industry']
    )
    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ Dữ liệu đã được chèn vào bảng base thành công!")
