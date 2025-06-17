# Dự Đoán Xu Hướng Việc Làm

## Mô Tả

Dự án "Dự đoán xu hướng việc làm" được xây dựng nhằm phân tích và dự báo xu hướng tuyển dụng trong các ngành nghề khác nhau tại Việt Nam thông qua dữ liệu thực tế thu thập từ trang tuyển dụng TopCV. Sử dụng kỹ thuật web scraping, hệ thống tự động thu thập thông tin việc làm như tiêu đề công việc, kỹ năng yêu cầu, địa điểm, mức lương và thời gian đăng tuyển. Dữ liệu sau khi thu thập được xử lý, chuẩn hóa và áp dụng các kỹ thuật xử lý ngôn ngữ tự nhiên (NLP) nhằm trích xuất thông tin giá trị. Các mô hình học sâu tiên tiến như Bi-LSTM (Bidirectional Long Short-Term Memory) và GRU (Gated Recurrent Unit) được triển khai để phát hiện xu hướng biến đổi theo thời gian, từ đó đưa ra dự đoán nhu cầu việc làm trong tương lai theo từng ngành nghề, khu vực và kỹ năng. Kết quả của dự án mang lại cái nhìn toàn diện và có chiều sâu về thị trường lao động, giúp người tìm việc định hướng nghề nghiệp phù hợp, đồng thời hỗ trợ các doanh nghiệp và tổ chức trong việc đưa ra chiến lược tuyển dụng hiệu quả. Bên cạnh đó, hệ thống được tích hợp với giao diện web thân thiện phát triển bằng Flask, cho phép người dùng truy cập, tra cứu và trực quan hóa dữ liệu xu hướng một cách dễ dàng và thuận tiện.

## Cài Đặt

1. Đầu tiên, bạn cần clone repository này về máy của mình:

2. Tiếp theo, cài đặt tất cả các thư viện Python cần thiết cho dự án bằng cách sử dụng pip:
   
2.1  Khởi tạo môi trường venv
2.2  Cài đặt các bảng trong database như link ở dưới  
2.3  pip install -r requirements.txt

4. Nhấn Flask run để chạy chương trình




### Các phần cần chú ý:
- **Link Database:** <https://dbdiagram.io/d/680a0a541ca52373f52dc88b>
- **Slide:**  <https://www.canva.com/design/DAGp815VW5c/rDQROYBAiggY_TyIAGPKOg/edit?utm_content=DAGp815VW5c&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton>
- **Report:** <https://docs.google.com/document/d/1-ONSGYVzXXBiLqZTSVZP8wsA4lx06plPfnFf7cN6aac/edit?usp=sharing>
  

