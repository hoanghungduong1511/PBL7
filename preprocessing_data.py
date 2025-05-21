import pandas as pd
import pymysql

# Đọc file Excel
df = pd.read_excel('jobs.xlsx', engine='openpyxl')

# Chuyển ngày về định dạng đúng
df['created_at'] = pd.to_datetime(df['created_at']).dt.date
df['experience'] = df['experience'].fillna(0)


# Kết nối MySQL
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',  # sửa lại theo thông tin thật
    database='pbl7',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()

# Insert từng dòng
for _, row in df.iterrows():
    sql = """
        INSERT INTO jobs (
            job_title, company_name, job_type,
            location, salary, experience, deadline,
            id_hr, industry
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        row['title'],
        row['company_name'],
        'offline',
        row['location'],
        row['salary'],
        row['experience'],
        row['created_at'],
        None,
        row['industry']
    )
    cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ Đã thêm dữ liệu Excel vào MySQL thành công!")
