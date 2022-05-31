from __future__ import print_function
import time
from sr.robot import *

"""
Exercise 1 python script

Put the main code after the definition of the functions. The code should drive the robot around the environment
Steps to be performed:
1- give a linear velocity (speed 50, time 2)
2- give an angular velocity (speed 20, time 2)
3- move the robot in circle -> hint: you should create a new function setting the velocities so as to have a linear velocity + an angular velocity (speed 30, time 5)

When done, run with:
	$ python run.py exercise1.py
"""

R = Robot()
""" instance of the class Robot"""

"""
global variables needed
"""
direction_tht = 10 #the angle-width for scanning
dist_tht = 0.01 #geting the angle through distance,this is the error tolerance
make_turn_tht = 1#front distance below which ,the robot will make a turn
turned_angle = 0 #angle turned in order to grab silver-token
last_s_dist = 0 #distance of silver token from last scanning
obstacle_tht = 0.9 #below which,front radar will take assume that robot need to make a turn
nearest_tht = 0.6	# below which, robot think it too close to an object
d_th = 0.39 # below which robot can grab the silver token
front_G_d = 100 #closest distance from the front
left_G_d = 100 #closest distance from the left
right_G_d = 100 #closest distance from the right
nearest_G_d = 100# closest distance from the wide-front
count_num_thre = 1 #a low-pass filter for the the changing of distance value, above which we thought as a effective data
silver_dist_de_count = 0 #to count the continueous decreasing times of the distance with the closest silver token
silver_dist_de_count_thr = 3#above which we take assume as a real decreasinhg of distance with silver-token, this is for filtering data purpose
count_f = 0 # works together with count_num_thre
count_l = 0# works together with count_num_thre
count_r = 0# works together with count_num_thre
count_a = 0# works together with count_num_thre
go_grab_flag = 1 #next silver token won't be the previous one
silver_scan_radar_radius = 2 #distance within such a range,we consider go and grab it
left_radar_angle = 15 #width of left scanning
right_radar_angle = 15#width
front_radar_angle = 10#width
count = 0
mini_dist = 100
def drive(speed, seconds):
    """
    Function for setting a linear velocity

    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    #print("forward a bit")
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

def turn(speed, seconds):
    """
    Function for setting an angular velocity
    
    Args: speed (int): the speed of the wheels
	  seconds (int): the time interval
    """
    R.motors[0].m0.power = speed
    R.motors[0].m1.power = -speed
    time.sleep(seconds)
    R.motors[0].m0.power = 0
    R.motors[0].m1.power = 0

#here goes the code
def find_silver_token():
    """
    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_SILVER:
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y
   	
def find_closest_golden_token():
    """
    Function to find the closest silver token

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    global mini_dist
    dist=100
    for token in R.see():
        if token.dist < dist and token.info.marker_type is MARKER_TOKEN_GOLD:
            dist=token.dist
	    rot_y=token.rot_y
    if dist<mini_dist:
	mini_dist = dist
    	f = open ('Closest_mine.txt','w')
    	f.write(str(mini_dist)+"\n")
    	f.close() 
    if dist==100:
	return -1, -1
    else:
   	return dist, rot_y

def find_golden_token_dist(angle1,ang_th_ta):
    if 1:
	global direction_tht
	global dist_tht 
	global make_turn_tht 
	global turned_angle 
	global last_s_dist 
	global obstacle_tht 	
	global a_th 
	global d_th 
    """
    Function to find the closest golden token in the direction of angle1 and an angle width of ang_th_ta

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """
    dist=100
    #abs_angle = 360
    for token in R.see():
        if angle1 - ang_th_ta <= token.rot_y <= angle1 + ang_th_ta and token.info.marker_type is MARKER_TOKEN_GOLD and token.dist < dist:
    	  #  print ("dist is ",token.dist,"rotate",token.rot_y)
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
    	
	return 100,0
	
    else:
   	return dist, rot_y

def check_golden_block(angle_tem):
 
    """
    Function to check if anything block us to grab the silver-token

    Returns:
	dist (float): distance of the blocking golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the blocking golden token (-1 if no golden token is detected)"""
	
    dist=100
    for token in R.see():
        if angle_tem - 20 <= token.rot_y <= angle_tem + 20 and token.info.marker_type is MARKER_TOKEN_GOLD and token.dist < dist :
    	    #print ("check block dist is ",token.dist,"rotate",token.rot_y)
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1,-1
	
    else:
   	return dist, rot_y

def check_golden_around(angle_tem):
    """
    Function to find the closest golden token in the direction of front and an angle width of 45 degree

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the golden token (-1 if no golden token is detected)
    """

    dist=100
    for token in R.see():
        if angle_tem - 45 <= token.rot_y <= angle_tem + 45 and token.info.marker_type is MARKER_TOKEN_GOLD and token.dist < dist:
    	    #print ("check block dist is ",token.dist,"rotate",token.rot_y)
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	return -1,-1
	
    else:
   	return dist, rot_y


def find_silver_token_angle(dist1):
    """
    Function to find the angle of a silver-token when given a distance for closed-loop control to rotate the robot pointing towards it

    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the silver token (-1 if no silver token is detected)
    """
    if 1:
   	global direction_tht
	global dist_tht 
	global make_turn_tht 
	global turned_angle 
	global last_s_dist 
	global obstacle_tht 	
	global a_th 
	global d_th     
    dist=100
    for token in R.see():
        if token.dist - dist_tht <= dist1 <= token.dist + dist_tht and token.info.marker_type is MARKER_TOKEN_SILVER:
    	  #  print ("dist is ",token.dist,"rotate",token.rot_y)
            dist=token.dist
	    rot_y=token.rot_y
    if dist==100:
	dist_tht = dist_tht*2
	return find_silver_token_angle(dist1)
    else:
    	dist_tht = 0.01
   	return dist, rot_y


def choose_turn():
        """
    Function to find the direction to make a turn,left or right

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the relevant golden token (-1 if no golden token is detected)
        """
	left_dist, left_angle = find_golden_token_dist(-90)
	right_dist, right_angle = find_golden_token_dist(90)
	if left_dist < right_dist:
		return right_dist,right_angle
	else:
		return left_dist, left_angle

def make_turn_locate_silver(dist1,angle1):
        """
    Function to rotate the robot towards the silver-token
        """
	global direction_tht
	global dist_tht 
	global make_turn_tht 
	global turned_angle 
	global last_s_dist 
	global obstacle_tht 	
	global a_th 
	global d_th 
	global front_G_d
	global op_G_d
	turned_angle = 0
	while 1:
		dist_here,angle_here = find_silver_token_angle(dist1)
		
		if not(-make_turn_tht<=angle_here<=make_turn_tht):
			#make_a_turn(5)
			
			turn(angle_here*0.1,1);
			turned_angle = turned_angle + angle_here*0.1
		else:
			#stop()
			tem_dist,tem_r = find_golden_token_dist(0,10)
			if tem_dist > front_G_d:
				turned_angle = 0
				#print("no need to turn back")
			break
			

def judge_last():
        """
    Function to judge if it is the previous token or if it is beyond the range

    Returns:
	dist (float): distance of the closest golden token (-1 if no golden token is detected)
	rot_y (float): angle between the robot and the relevant golden token (-1 if no golden token is detected)
        """
	global direction_tht
	global dist_tht 
	global make_turn_tht 
	global turned_angle 
	global last_s_dist 
	global obstacle_tht 	
	global a_th 
	global d_th 
	global go_grab_flag
	global silver_dist_de_count_thr
	global silver_dist_de_count
	dits_here, angle_here = find_silver_token()
	if dits_here > 1.5:
		go_grab_flag = 1
		last_s_dist = dits_here 
		return 1
	else:
		if dits_here - last_s_dist >= 0 and go_grab_flag == 0:
			#print("previous silver token",dits_here,last_s_dist,go_grab_flag)
			last_s_dist = dits_here                    #update last_dist
			return 1
		else:
			if silver_dist_de_count > silver_dist_de_count_thr:
				silver_dist_de_count = 0
				last_s_dist = dits_here                    #update last_dist
				return 0
			else:
				silver_dist_de_count = silver_dist_de_count + 1
				return 1
def scan_nearby_silver():
	
	"""
    Function to check if there is any grabable silver-token around robot 
    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the relevant silver token (-1 if no silver token is detected)
       """
	
	global dist_tht 
	global make_turn_tht 
	global turned_angle 
	global last_s_dist 
	global obstacle_tht 	
	global a_th 
	global d_th 
	global front_G_d
	global op_G_d
	#print("scanning nearest silver")
	if judge_last():
		
		return -1,-1
	else: 
		#print("not the previous silver")
		dist_nearest_silver, rot_y_nearest_silver = find_silver_token()
		#print("nearest silver dist  ",dist_nearest_silver,rot_y_nearest_silver)
		
		if 1:
			dist_here_mid_golden, rot_y_mid_golden = check_golden_block(rot_y_nearest_silver)
			#print("checking block mid _dist ",dist_here_mid_golden)
			if dist_here_mid_golden <= dist_nearest_silver:
				#print("something in our way to grab the closest")
				return -1,-1
			else:
				#print("find ya",dist_nearest_silver,rot_y_nearest_silver)
				return  dist_nearest_silver, rot_y_nearest_silver
		else:
			return -1,-1




def capture_token(dist_s_new,rot_y_s_new): #go capture a silver token

 	"""
    Function to head foward to grab a silver token and put it back and return direction. when silver token come into a specific range we go and grab it. Then return some angle, since we changed our direction in order to capture the silver.
    Returns:
	dist (float): distance of the closest silver token (-1 if no silver token is detected)
	rot_y (float): angle between the robot and the relevant silver token (-1 if no silver token is detected)
    """
	global go_grab_flag
	global last_s_dist
	make_turn_locate_silver(dist_s_new,rot_y_s_new)
	while 1:
		dist, rot_y = find_silver_token()
		if dist < d_th:# if we are close to the token, we try grab it.
			print("try grab");
       		if R.grab():       				
           			stop()
           			#print("Gotcha!")
           			time.sleep(0.5)
	   			turn(65, 1)
	   			time.sleep(0.5)
	   			R.release()
	   			turn(-65,1)
	   			turn(-turned_angle,1);
	   			dist, rot_y = find_silver_token()
				last_s_dist = dist			#remember the distance of the previous token	
				go_grab_flag = 0
				return
		else:
        		#print("Aww, I'm not close enough.")
        		go_ahead()
        		time.sleep(0.002)
 
def go_ahead():
        """
    Function to start the engine of the robot
    """
	R.motors[0].m0.power = 50
    	R.motors[0].m1.power = 50

def stop():
	"""
    Function to stop the engine of the robot
    """
	R.motors[0].m0.power = 0
    	R.motors[0].m1.power = 0


def make_a_turn(magnitude):
	"""
    	Function to create difference between left and right engine in order to make turn
   	 """
	R.motors[0].m0.power = R.motors[0].m0.power + magnitude
    	R.motors[0].m1.power = R.motors[0].m0.power - magnitude

def radar_detect_around(): 
# function to update the closest object in our left,right,front,wide_front directions
	global front_G_d
	global left_G_d
	global right_G_d 
	global count_num_thre
	global count_f
	global count_l
	global count_r
	global count_a
	global left_radar_angle 
	global right_radar_angle 
	global front_radar_angle 
	global nearest_G_d
	
	front_d,front_r = find_golden_token_dist(0,front_radar_angle)# closest obeject in the front
	if front_G_d > front_d or count_f > count_num_thre:
		if front_d != 100:
			front_G_d = front_d
			count_f = 0
	else:
		if front_d != 100:
			count_f = count_f +1
			
	left_d,letf_r = find_golden_token_dist(-90,left_radar_angle)# closest obeject on the  left
	if left_G_d > left_d or count_l > count_num_thre:
		if left_d != 100:
			left_G_d = left_d
			count_l = 0
	else:
		if left_d != 100:
			count_l = count_l +1
	
	right_d,right_r = find_golden_token_dist(90,right_radar_angle)# closest obeject on the  right
	if right_G_d > right_d or count_r > count_num_thre:
		if right_d != 100:
			right_G_d = right_d
			count_r = 0
	else:
		if right_d != 100:
			count_r = count_r +1
			
	around_d,around_r = find_golden_token_dist(0,75)
	if nearest_G_d > around_d or count_a > count_num_thre:# closest obeject in the wide-front
		if around_d != 100:
			nearest_G_d = around_d
			count_a = 0
	else:
		if around_d != 100:
			count_a = count_a +1
			
			
	#print("current pos",front_G_d,left_G_d,right_G_d,"current count_th",count_num_thre)

def check_turn():   #check if there is a corner or other obstacle around of us
	global nearest_G_d
	global front_G_d
	radar_detect_around()
	if nearest_G_d <= nearest_tht or front_G_d < obstacle_tht:
	#avoid much close to any object so robot need to stop and make turn
		stop()
		if left_G_d < right_G_d:
			turn(3,1)
			nearest_G_d = 100 #let robot able to try to move a little
			check_turn()
		else:
			turn(-3,1)
			nearest_G_d = 100

def navigate():
	"""this is for navigation to allow our robot able to move along the track"""
	global count
	go_ahead()
	time.sleep(0.002)
	if count % 5 == 0:
		find_closest_golden_token()
	radar_detect_around() #update datas
	radar_detect_around()	
	if right_G_d > left_G_d:  #an closedloop control to make our robot on the middle of the road
		make_a_turn((right_G_d/left_G_d)*2)
	else:
		make_a_turn(-(left_G_d/right_G_d)*3)
	time.sleep(0.001)
	check_turn()       #check if we meet a corner, if yes,it will make turn
	
def grab_mission():
	"""this is for excecuting our grab mission"""
	dist_s_new,rot_y_s_new = scan_nearby_silver()
	if dist_s_new != -1:
		stop()
		capture_token(dist_s_new,rot_y_s_new) 
			
f = open ('Closest_mine.txt','w')
f.write(str(mini_dist)+"\n")
f.close() 			
go_ahead()
while 1:
	navigate() #this if for the navigation of robot to move along the track
	grab_mission() 
	
	
			




