from datetime import datetime, timedelta


data = [(1234, 'Колбаса', '27.09.23'), (21163, 'Cыр Радомер', '26.09.23')]


sorted_data = sorted(data, key=lambda x: datetime.strptime(x[2], "%d.%m.%y"))

print(sorted_data)
