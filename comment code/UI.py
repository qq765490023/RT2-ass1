#!/usr/bin/env python3


## @package 
# \file UI.py
# \brief This file contains the code of RT_3 assignment
# \author Zhouyang Hong
# \version 1.0
# \date 17/05/2022
#
# \details
# Subscribes to: /scan
# For geeting the informations about environment
#
# Publishes to: cmd_vel and /move_base/goal
# For setting the speed of robot and input a a target and the robot moves to there.
#
# Node name: UI
# 
#
# Description:
# This is a program consists of three main modules which are 
#  1. input and go to a target
#  2. controlled manually by keyboard
#  3. controlled by keyboard but hitting obstacles is avoided internally.
#   For using them just run this program and follow the instructions shows up.


import time
import rospy
from getkey import getkey, keys
from geometry_msgs.msg import Twist
from move_base_msgs.msg import MoveBaseActionGoal
from sensor_msgs.msg import LaserScan

##
# \var pub_vel 
#   This variable is a object for making the robot move
pub_vel = rospy.Publisher("cmd_vel", Twist) 
##
# \var pub_goal 
#   This variable is a obeject can be used to move the robot to an objective position
pub_goal = rospy.Publisher("/move_base/goal", MoveBaseActionGoal)
##
# \var CA_status 
#   This variable is for knowing the status of obstacles around the robot which allows me setting strategies to avoid obstacles
CA_status = -1
##
# \var state_description
#   This is for showing the info of CA_status
state_description = ''
##
# \var vel
#   This is a variable that can be used for knowing the speed information of robot.
vel = Twist()

##
# \brief Identify obstacles around robot
# \param The data from scan which is data about the environment
# \return ..
# \details This is the laser data callback,and will be called any time when receiced scan data. 
#   the emergence brake is set inside this part. The scan data are divided into 5 ranges and take the minimum then being further processed for letting robot knows curren state.
#
def clbk_laser(msg):   regions = {
        'right':  min(min(msg.ranges[0:143]), 10),
        'fright': min(min(msg.ranges[144:287]), 10),
        'front':  min(min(msg.ranges[288:431]), 10),
        'fleft':  min(min(msg.ranges[432:575]), 10),
        'left':   min(min(msg.ranges[576:719]), 10),
    }
    take_action(regions)
##
# \brief Repredenting obstacles and emergency stop.
# \param The distance of the closest obeject around the robot in 5 directions
# \return ..
# \details 
#   This functions is for representing the distributions of obstacles around the robot with specific number. 
#   CA_status will be updated according to the current situation. Emergency stop is achieved here
def take_action(regions): 
    global CA_status
    global state_description
    global vel
    if regions['front'] > 1 and regions['left'] > 1 and regions['right'] > 1:
        state_description = 'case 1 - OK'
        CA_status = 1
    elif regions['front'] < 1 and regions['left'] > 1 and regions['right'] > 1:
        state_description = 'case 2 - front_disable'
        CA_status = 2
    elif regions['front'] > 1 and regions['left'] > 1 and regions['right'] < 1:
        state_description = 'case 3 - right_disable'
        CA_status = 3
    elif regions['front'] > 1 and regions['left'] < 1 and regions['right'] > 1:
        state_description = 'case 4 - left_disable'
        CA_status =4
    elif regions['front'] < 1 and regions['left'] > 1 and regions['right'] < 1:
        state_description = 'case 5 - front_right_disable'
        CA_status = 5
    elif regions['front'] < 1 and regions['left'] < 1 and regions['right'] > 1:
        state_description = 'case 6 - front_left_disable'
        CA_status = 6
    elif regions['front'] < 1 and regions['left'] < 1 and regions['right'] < 1:
        state_description = 'case 7 - backward allowed'
        CA_status = 7
    elif regions['front'] > 1 and regions['left'] < 1 and regions['right'] < 1:
        state_description = 'case 8 - left_right_disable'
        CA_status = 8
    else:
        state_description = 'unknown case'
    if regions['front'] < 1 and vel.linear.x >0: #emergency brake
      vel.linear.x = 0
      pub_vel.publish(vel) 
##
# \brief Control robot with keyboard
# \param ..
# \return ..
# \details This function is for the control of robot by using keyboard everything is done by user.
def KB_control():
  print('please input the command:\nw: move forward and speed up\ns: stop\nx: backward\na: turn left\nd: turn right\nq: quit\n')
  vel = Twist()
  while True:  # making a loop
    time.sleep(0.01)
    key = getkey()
    if True:
        if key == 'w':
            vel.linear.x =  1
        elif key == 's':
            vel.linear.x = 0
        elif key == 'x':
            vel.linear.x = -1
        elif key == 'a':
            vel.angular.z = 10
            pub_vel.publish(vel)
            time.sleep(0.1)
            vel.angular.z = 0
        elif key == 'd':
            vel.angular.z = -10
            pub_vel.publish(vel)
            time.sleep(0.1)
            vel.angular.z = 0
        elif key == 'q':
            break 
        
    pub_vel.publish(vel)     
##
# \brief Control robot with keyboard equipped with internal collision avoidance
# \param ..
# \return ..
# \details This function is to control the robot with keyboard while equipped with function of avoiding hitting obstacles
#
def KB_control_collision_avoidance(): 
  global CA_status
  print('please input the command:\nw: move forward and speed up\ns: stop\nx: backward\na: turn left\nd: turn right\nq: quit\n')
  global vel
  while True:  # making a loop
    time.sleep(0.01)
    key = getkey()
    if True:
        if key == 'w':
          if CA_status==2 or CA_status==5 or CA_status==6 or CA_status==7: 
            vel.linear.x = 0
          else:
            vel.linear.x = 1
        elif key == 's':
            vel.linear.x = 0
        elif key == 'x':
            vel.linear.x = -1
        elif key == 'a':
          if (CA_status==4 or CA_status==6 or CA_status==7 or CA_status==8) and vel.linear.x != 0 :
              vel.angular.z = 0
          else:
            vel.angular.z = 10
            pub_vel.publish(vel)
            time.sleep(0.1)
            vel.angular.z = 0
        elif key == 'd':
          if (CA_status==3 or CA_status==5 or CA_status==7 or CA_status==8) and vel.linear.x != 0 :
             vel.angular.z = 0
          else:
            vel.angular.z = -10
            pub_vel.publish(vel)
            time.sleep(0.1)
            vel.angular.z = 0
        elif key == 'q':
            print('You Pressed q!')
            break 
    pub_vel.publish(vel) 
##
# \brief Reach the desired goal inputed by user.
# \param ..
# \return ..
# \details By calling this function, users will be asked to input a target point and then the robot will move there in case of possible
#
def mov_goal():  #
  pos = MoveBaseActionGoal()
  while True: 
   x, y = [float(x) for x in input("Enter target x and y in format:x y\nor input:-100 -100 to quit \n").split()]
   if x==-100:
    break
   print("heading to :"+str(x)+","+str(y))
   pos.goal.target_pose.pose.orientation.w = 1
   pos.goal.target_pose.header.frame_id = 'map'
   pos.goal.target_pose.pose.position.y = x
   pos.goal.target_pose.pose.position.x = y
   pub_goal.publish(pos)
##
# \brief Main function
# \param 
# \return 
# \details Inside this main function, user will be asked to choose the desired functionality within 3 options. Which are ask and go, controlled with keyboard and controlled by keyboard but equipped with obstacle avoidance.
def main()
 rospy.init_node("UI")
 sub_scan = None
 while True:
  a = input("select option\n 1:input target and go reach there \n 2:control by keyboard \n 3:control by keyboard with collision-avoidance\n 4:quit \n" )
  if a=='1':
   mov_goal() #set a goal and reach there
  if a=='2':
   KB_control() #control with keyboard
  if a=='3':
   sub_scan = rospy.Subscriber('/scan', LaserScan, clbk_laser)
   KB_control_collision_avoidance() #control with keyboard and assisted with collision avoidance
  if a=='4':
   break
  pass
 rospy.spin()


if __name__ == "__main__"
	main()
	
	
	
	
	
	
	
	
	
