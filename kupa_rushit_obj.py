# POLYGONS
PARKING_POLYGON = ''
SUPER_MARKET_POLYGON = ''
CASHE_REGISTERS_POLYGON = ''
BUTCHERY_POYLYGON = ''
WAREHOSE_POLYGON = ''

# OPENING_HOURS
SUNDAY_OP = '07:30'
SUNDAY_CL = '21:00'
MONDAY_OP = '07:30'
MONDAY_CL = '21:00'
TUSDAY_OP = '07:30'
TUSDAY_CL = '21:00'
WEDNESDAY_OP = '07:30'
WEDNESDAY_CL = '22:00'
THURDSDAY_OP = '07:30'
THURDSDAY_CL = '22:00'
FRIDAY_OP = '07:00'
FRIDAY_OP = '15:00'
# not working in saterday

hilidays = ["2024/01/01", "2024/05/26"] # days without work
spicial_days = ["2024/01/21", "2024/01/26"] # days with more workers and customers


class person:
    def __init__(self):
        pass
    def vacation(self):
        """
        vacation will get list of dates and in these dates there will be no data
        """
        pass
    def one_day_before_vacation(self):
        """
        there will be more workers and more customers
        """
        pass
    def entering_market(self):
        """
        because we work with geolocated data we want to let the analyst to know when the object come into the supermarket
        for that we create the parking lot data - almost every customer will get detected in the parking lot before it entering the supermarket
        note that will be customers that will not detect in the parking lot for making a bit noise for the students
        """
        pass
# workers
class worker(person):
    pass

class manerger(worker):
    pass # comes from 8 to 5 and not moving much

class cashier(worker):
    pass

class butcher(worker):
    pass

class delivery_guy(worker):
    pass

class general_worker(worker):
    pass

class securiy_guy(worker):
    pass

# customers
class cursomer(person):
    pass
    def purchase(self):
        """
        function to insert log of customer bill
        """
        pass

class repeat_customer(customer):
    pass

class one_time_customer(customers):
    pass

class no_phone(customer):
    pass # 20 a day

class not_paying(castomer):
    pass # childrens and peaple -- 20 a day