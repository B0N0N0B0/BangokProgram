import datetime
d = datetime.datetime.strptime('30421225', '%Y%m%d')
d = d.date()
print(type(d))
print(d)

da = datetime.datetime.strptime('20221224', '%Y%m%d')
da = da.date()
print(da)

dda = d-da
print(dda)
print(dda.days)

dt = datetime.datetime.now()
dt = dt.date()
print(dt)

dt = dt-dda
print(dt)

t = datetime.datetime.strptime('20230120', '%Y%m%d')
t = t.date()
dts1 = (d-t).total_seconds()
dts2 = (t-da).total_seconds()
print(dts1,dts2)