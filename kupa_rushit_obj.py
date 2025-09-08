# POLYGONS
PARKING_POLYGON = 'polygon(i will fll it later)'
SUPER_MARKET_POLYGON = 'polygon(i will fll it later)'
CASHE_REGISTERS_POLYGON = 'polygon(i will fll it later)'
BUTCHERY_POYLYGON = 'polygon(i will fll it later)'
WAREHOSE_POLYGON = 'polygon(i will fll it later)'
HEAD_OFFICE = 'polygon(i will fll it later)'

# OPENING_HOURS
SUNDAY_OP = '07:30'
SUNDAY_CL = '21:00'
MONDAY_OP = '07:30'
MONDAY_CL = '21:00'
TUSDAY_OP = '07:30'
TUSDAY_CL = '21:00'
WEDNESDAY_OP = '07:30'
WEDNESDAY_CL = '22:00'
THURSDSDAY_OP = '07:30'
THURSDSDAY_CL = '22:00'
FRIDAY_OP = '07:00'
FRIDAY_OP = '15:00'
# not working in saterday

hilidays = ["2024/01/01", "2024/05/26"] # days without work
spicial_days = ["2024/01/21", "2024/01/26"] # days with more workers and customers

# geolocation
"""
each minute there will be a ramdom statistic of 40% precent that a person is geting detected
"""


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
    """
    comes from around ~8:00 in the morning untill ~17:00
    usually in her office
    makes a tour twice a day in the office
    when the maneger in cavation there is a replacment (new id) that comes from 8 to 5. the maneger gows one time to vacation of week and one day off
    """
    pass # comes from 8 to 5 and not moving much

class cashier(worker):
    """
    a shift of cashier is 6-8 hours it an be from 8- 17:00 or 13:00 - 21:00 according to the day
    each time there are at least 2 cashiers up to 5 (most of the time 3 cashiers). in thursday : from 16:00 - 20:00 there are 5 casherers
    in friday there are 5 cashiers from 8 to 14:00.
    the cashier is mostly in the CASHE_REGISTERS_POLYGON
    overall there are 15 different casherers that can go to shifts
    """
    pass

class butcher(worker):
    """
    the buchery is open in sunday to thursday from 10:00 - 19:00, in friday from 9:00 to 14:00
    all time the buchery is open there are 2 employees each time
    there are all in all 4 buchers that can fulfill the shifts
    """
    pass

class delivery_guy(worker):
    """
    the delivery guy comes at ~6:00 AM at monday and thursday and leaves around ~6:30
    there are 8 different delivery guys
    """
    pass

class general_worker(worker):
    """
    there are overall 10 general_workers, but in every shift there are 2 general workers
    they walk around the market from 8:00 to 20:00 in sunday to wednesday
    in thursday they stay untill 22:00
    in friday they stay 15:00
    
    """
    pass
class senior_general_worker(worker):
    """
    there is one senior general worker that cames around 6:30 each day and leaves at 20:00.
    at monday and thursday he comes at 6 with the delivery guy
    he comes every day
    """
    pass

class securiy_guy(worker):
    """
    the security guy comes at opening and leaves at the closing he not moving much he get detected in the parking and the market and he will have 
    Low accuracy range - the accuracy is big so the geolocation is not that accurate
    there are 4 security gys
    """
    pass

# customers
class cursomer(person):
    pass
    def purchase(self):
        """
        function to insert log of customer bill
        the function get as input time of stay (from stay_time func)
        and return number of the bill in New Shekels with 17% precent
        the time of the purchase will be the last timestamp at cashier_zone_area
        """
        pass
    def stay_time(self):
        """
        function that will calculate hou much the customer is in the market - the more it stay the more it purchase
        """
        pass

class repeat_customer(customer):
    """
    customer that comes twice a week in thursday/friday and some day in sunday - wednesday. they stay more in thursday/friday
    """
    pass # 100 overall

class one_time_customer(customers):
    """
    comes once in 2 month
    """
    pass # 3-7 per day

class no_phone(customer):
    """
    has onlly function of purchase
    """
    pass # 15-25 a day

class not_paying(castomer):
    """
    childs or peaple that don't want to buy but have phone - only geolocation data
    """
    pass # childrens and peaple -- 10-35 a day