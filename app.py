from flask import Flask, render_template, request
app = Flask(__name__)

# constants used
no_of_stops = 3602
no_of_routes = 550
no_of_stop_seq = 100

# opening all input files
rt_fd = open("routes.txt", "r")
st_fd = open("stop_times.txt", "r")
s_fd = open("stops.txt", "r")
tr_fd = open("trips.txt", "r")

# flag is to ignore first line in the files, header line
flag = 0
# Reading stops.txt & storing all stops name in stop[]
stop = [0 for i in range(no_of_stops)]

# inp[] is to store stop names for drop down menu
# as stop[] contains holes due to some missing stops :: anomaly
inp = []
j = 0
for x in s_fd:
    if flag == 0:
        flag = 1
    else:
        if x != '\n':
            x = x.rstrip('\n')
            arr = x.split(',')
            stop[int(arr[0])] = arr[2]
            j = j+1
            inp.append(arr[2])

# Reading routes.txt & storing route names corresponding to route_id
routeName = [0 for i in range(no_of_routes)]
flag = 0
for x in rt_fd:
    if flag == 0:
        flag = 1
    else:
        if x != '\n':
            x = x.rstrip('\n')
            arr = x.split(',')
            routeName[int(arr[3])] = arr[1]


# Reading trips.txt file to store trip_ids corresponding to each route_id in RouteToTripTbl[]
RouteToTripTbl = [[] for i in range(no_of_routes)]

flag = 0
for x in tr_fd:
    if flag == 0:
        flag = 1
    else:
        if x != '\n':
            arr = x.split(',')
            RouteToTripTbl[int(arr[0])].append(int(arr[2]))


flag = 0

# Route_data[][] to store sequence wise stop_ids of each Route
Route_data = [[-1 for i in range(no_of_stop_seq)] for j in range(no_of_routes)]

# Reading stop_times.txt file to store stop_ids in a route & ignoring all other trip data
# Bascially, storing route data corresponding to one trip and ignoring all other trips
# as we need only routes from source to destination(ignoring trip times)
# while reading it is also taken care missing trips corresponding to each route :: anomaly
i = 0
curr_trip_store = 0
next_trip_store = RouteToTripTbl[1][0]
for y in st_fd:
    if flag == 0:
        flag = 1
    else:
        if y != '\n':
            y = y.rstrip('\n')
            arr = y.split(',')
            if int(arr[0]) != curr_trip_store and next_trip_store == -1:
                break
            if int(arr[0]) > next_trip_store and next_trip_store != -1:
                save = 0
                for j in range(len(RouteToTripTbl[i])):
                    if RouteToTripTbl[i][j] == int(arr[0]):
                        save = 1
                        break
                if save == 0:
                    i = i+1
                next_trip_store = int(arr[0])

            if int(arr[0]) == next_trip_store:
                curr_trip_store = next_trip_store
                i = i + 1
                if len(RouteToTripTbl[i + 1]) == 0:
                    next_trip_store = -1
                else:
                    next_trip_store = RouteToTripTbl[i+1][0]

            if int(arr[0]) == curr_trip_store:
                Route_data[i][int(arr[4])] = int(arr[3])

# Route_info to prepare route_id & stop seq no pair for each matching source & destination
class Route_Info:
    id = 0
    seqNo = 0

    def __init__(self, val, val1):
        self.id = val
        self.seqNo = val1

# Class to store one hop routes having start route_id, destination route_id & interchanging stop_id
class One_hop_Route_Info:
    id1 = 0
    id2 = 0
    stop_id = 0

    def __init__(self, var1, var2, var3):
        self.id1 = var1
        self.id2 = var2
        self.stop_id = var3

# class to have all (0 & 1) hop route information having start stop, start route name, interchanging stop_name
# destination stop name , destination route name
class output:
    startName = 0
    startRouteName = 0
    midStop = 0
    destName = 0
    destRouteName = 0

    def __init__(self, a, b, c, d, e):
        self.startName = a
        self.startRouteName = b
        self.midStop = c
        self.destName = d
        self.destRouteName = e

# Function to calculate 0 & 1 hop routes for given start & destination
def FindRoute(start, dest):
    start_id = 0
    dest_id = 0

    for i in range(len(stop)):
        if stop[i] == start:
            start_id = i
        if stop[i] == dest:
            dest_id = i

# list1[] is array of class Route_Info to store all route_ids and sequence no. corresponding to start location
    list1 = []
    for i in range(len(Route_data)):
        for j in range(len(Route_data[i])):
            if Route_data[i][j] == start_id:
                tc = Route_Info(i, j)
                list1.append(tc)

# list2[] is array of class Route_Info to store all route_ids and sequence no. corresponding to destination location
    list2 = []
    for i in range(len(Route_data)):
        for j in range(len(Route_data[i])):
            if Route_data[i][j] == dest_id:
                tc = Route_Info(i, j)
                list2.append(tc)

# list3[] is array of integers storing those route_ids of zero hop routes
    list3 = []
    for i in range(len(list1)):
        for k in range(len(list2)):
            if list1[i].id == list2[k].id and list1[i].seqNo <= list2[k].seqNo:
                list3.append(list1[i].id)

# list4[] is array of class One_hop_Route_Info containing data for 1 hop route
    list4 = []
    for i in range(len(list1)):
        for j in range(len(list2)):
            if list1[i].id != list2[j].id:
                for k in range(list1[i].seqNo, len(Route_data[list1[i].id])):
                    if Route_data[list1[i].id][k] == -1:
                        break
                    for l in range(0, list2[j].seqNo):
                        if Route_data[list1[i].id][k] == Route_data[list2[j].id][l]:
                            tmp = One_hop_Route_Info(list1[i].id, list2[j].id, Route_data[list1[i].id][k])
                            list4.append(tmp)

# RouteOutput[] is array of class Output containing all possible routes for given start and destination
    RouteOutput = []
    for i in range(len(list3)):
        outObj = output(start, routeName[list3[i]], " ----- ", dest, routeName[list3[i]])
        RouteOutput.append(outObj)

    for i in range(len(list4)):
        outObj = output(start, routeName[list4[i].id1], stop[list4[i].stop_id], dest, routeName[list4[i].id2])
        RouteOutput.append(outObj)

    return RouteOutput



@app.route('/')
def mainpage():
    inp.sort()
    return render_template('mainView.html', input=inp)


@app.route('/ShowRoutes', methods=['POST', 'GET'])
def showroutes():
    if request.method == 'POST':
        start = request.form.get("start")
        dest = request.form.get("dest")
        arrAns = FindRoute(start, dest)
        if len(arrAns)==0:
            return render_template("Routes2.html")
        else:
            return render_template("Routes.html", inputRoute=arrAns)


if __name__ == '__main__':
    app.debug = True
    app.run()
