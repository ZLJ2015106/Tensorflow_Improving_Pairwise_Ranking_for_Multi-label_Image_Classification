
import numpy as np
import tensorflow as tf

import inception_resnet_v2.inception as inception

from Define import *

init_fn = tf.contrib.layers.xavier_initializer()

def Global_Average_Pooling(x, stride=1):
    return tf.layers.average_pooling2d(inputs=x, pool_size=np.shape(x)[1:3], strides=stride)

def Image_Tagging(x, is_training, classes, decision_model = False):
    predict_dic = {}
    x = x / 127.5 - 1
    
    with tf.contrib.slim.arg_scope(inception.inception_resnet_v2_arg_scope()):
        logits, end_points = inception.inception_resnet_v2(x, is_training = is_training)

    # for key in end_points.keys():
    #     print(key, end_points[key])
    # input()
    
    predict_dic['LSEP'] = end_points['Logits'][:, :classes]
    
    if decision_model:
        with tf.variable_scope('Label_Decision'):
            x = tf.layers.batch_normalization(predict_dic['LSEP'], training = is_training)
            x = tf.nn.relu(x)
            share_feature_maps = x

            # Confidence
            x = tf.layers.dense(share_feature_maps, classes, kernel_initializer = init_fn)
            x = tf.nn.relu(x)
            x = tf.layers.dropout(x, rate = 0.5, training = is_training)
            
            conf_logits = tf.layers.dense(x, classes, kernel_initializer = init_fn)
            predict_dic['Confidence'] = tf.nn.sigmoid(conf_logits, name = 'conf/sigmoid')
            
            # TopK
            x = tf.layers.dense(share_feature_maps, 100, kernel_initializer = init_fn)
            x = tf.nn.relu(x)
            
            topk_logits = tf.layers.dense(x, MAX_TOP_K, kernel_initializer = init_fn)
            predict_dic['TopK'] = tf.nn.softmax(topk_logits, axis = -1, name = 'topk/softmax')
    
    return predict_dic

if __name__ == '__main__':
    input_var = tf.placeholder(tf.float32, [None, 299, 299, 3], name = 'images')
    
    predict_dic = Image_Tagging(input_var, False, 1000, decision_model = False)
    print(predict_dic)

