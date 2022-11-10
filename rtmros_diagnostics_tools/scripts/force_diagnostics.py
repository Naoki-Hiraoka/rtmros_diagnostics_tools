#!/usr/bin/env python
import rospy
import time
import copy
from geometry_msgs.msg import WrenchStamped
from diagnostic_msgs.msg import *

is_data_unchanged = False
prev_msg = WrenchStamped()

def topic_cb(msg) :
    global is_data_unchanged, prev_msg
    if prev_msg.wrench.force.x == msg.wrench.force.x and\
       prev_msg.wrench.force.y == msg.wrench.force.y and\
       prev_msg.wrench.force.z == msg.wrench.force.z and\
       prev_msg.wrench.torque.x == msg.wrench.torque.x and\
       prev_msg.wrench.torque.y == msg.wrench.torque.y and\
       prev_msg.wrench.torque.z == msg.wrench.torque.z:
        is_data_unchanged = True
    else:
        is_data_unchanged = False
    prev_msg = msg

if __name__ == '__main__':
    try:
        rospy.init_node('force_diagnostics')
        sub = rospy.Subscriber('~input', WrenchStamped, topic_cb, queue_size = 1)
        pub = rospy.Publisher('diagnostics', DiagnosticArray, queue_size = 1)
        name = rospy.get_param('~name','force')

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
