from datetime import datetime, timedelta


current_datetime = datetime.now()


print(datetime.strptime("23.09.23", "%d.%m.%y").strftime("%d.%m.%y") == current_datetime.strftime("%d.%m.%y"))
print(type(current_datetime.strftime("%d.%m.%y")))
