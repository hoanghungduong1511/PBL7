import torch
model_path = r"D:\My folder\HK8\PBL7\SRC\apps\charts\models\Model_BiLSTM_Attention_Trend.keras"
obj = torch.load(model_path, weights_only=False)
print(type(obj))