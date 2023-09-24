from datetime import datetime, timedelta


current_datetime = datetime.now()


# print(datetime.strptime("23.09.23", "%d.%m.%y") - current_datetime)
print(abs((current_datetime - datetime.strptime("28.09.23", "%d.%m.%y")).days))
# print(type(current_datetime.strftime("%d.%m.%y")))
