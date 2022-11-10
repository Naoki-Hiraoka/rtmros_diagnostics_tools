#!/usr/bin/env python
import rospy
import time
import copy
from nav_msgs.msg import Odometry
from diagnostic_msgs.msg import *

is_data_unchanged = False
prev_msg = Odometry()

def topic_cb(msg) :
    global is_data_unchanged, prev_msg
    if prev_msg.pose.pose.position.x == msg.pose.pose.position.x and\
       prev_msg.pose.pose.position.y == msg.pose.pose.position.y and\
       prev_msg.pose.pose.position.z == msg.pose.pose.position.z and\
       prev_msg.pose.pose.orientation.x == msg.pose.pose.orientation.x and\
       prev_msg.pose.pose.orientation.y == msg.pose.pose.orientation.y and\
       prev_msg.pose.pose.orientation.z == msg.pose.pose.orientation.z and\
       prev_msg.pose.pose.orientation.w == msg.pose.pose.orientation.w:
        is_data_unchanged = True
    else:
        is_data_unchanged = False
    prev_msg = msg

if __name__ == '__main__':
    try:
        rospy.init_node('odom_diagnostics')
        sub = rospy.Subscriber('~input', Odometry, topic_cb, queue_size = 1)
        pub = rospy.Publisher('diagnostics', DiagnosticArray, queue_size = 1)
        name = rospy.get_param('~name','odom')

        r = rospy.Rate(1) # 1hz
        while not rospy.is_shutdown():
            diagnostic = DiagnosticArray()
            diagnostic.header.stamp = rospy.Time.now()

            status = DiagnosticStatus()
            status.name = name
            if (rospy.Time.now() - prev_msg.header.stamp).to_sec() > 5.0:
                status.level = DiagnosticStatus.ERROR
                status.message = "topic is not arrived"
            elif is_data_unchanged:
                status.level = DiagnosticStatus.ERROR
                status.message = "data is not changed"
            else:
                status.level = DiagnosticStatus.OK
                status.message = ""
            diagnostic.status.append(status)
            pub.publish(diagnostic)
            r.sleep()
    except rospy.ROSInterruptException: pass
