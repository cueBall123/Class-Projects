/* 
 * File:   Handgesture.cpp
 * Author: cue
 *
 * Created on 10 April, 2014, 5:05 PM
 */
#include <cstdlib>
#include <opencv2/imgproc/imgproc.hpp>
#include "opencv2/highgui/highgui_c.h"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/contrib.hpp"
#include <math.h>
#include <cv.h>
#include <highgui.h>
#include <iostream>
#include <set>
#include <fstream>
#define _USE_MATH_DEFINES
 enum {
        GSD_HUE_LT = 3,
        GSD_HUE_UT = 33,
        GSD_INTENSITY_LT = 15,
        GSD_INTENSITY_UT = 250
    };
int xvalue,yvalue = 0;

int refreshFlag=0; // indicate whether the display needs to be refreshed


using namespace std;
using namespace cv;
vector<vector<Point> >  create_contours(Mat3b  );
Mat createbwhist(Mat,float* );
void CallBackFunc(int event, int x, int y, int flags, void* userdata)
{
    
            if  ( event == EVENT_LBUTTONDOWN )
        {
                  cout << "Left button of the mouse is clicked - position (" << x << ", " << y << ")" << endl;
                  xvalue = x;yvalue = y;
                  refreshFlag=1;
        }  
    }

void changevalhandl(int pos){
    refreshFlag=1;
    }

int findBiggestContour(vector<vector<Point> > contours){
    int iBiggestContour = -1;
    int sBiggestContour = 0;
    for (int i = 0; i < contours.size(); i++){
        if(contours[i].size() > sBiggestContour){
            sBiggestContour = contours[i].size();
            iBiggestContour = i;
        }
    }
    return iBiggestContour;
}
/*
 * 
 */
VideoCapture cap(0);
int hmin,hmax,smin,smax,vmin,vmax;
int detect_gesture(char);
int calibrate_skincolor();
int threshold_chrom = 0;
 Mat bw;
 
int main(int argc, char** argv)
    {
    
    //calibrate_skincolor();
    
     char mode = 'f';
    if(argc !=2)
        {
        cout<<"The usage is <-c/h/H>"<<endl;
        cout<<"-c : Contour matching"<<endl;
        cout<<"-h : Histogram matching"<<endl;
        cout<<"-H : ConvexHull defects"<<endl;
        }
    else{
        mode = argv[1][1];
        cout<<mode;
    detect_gesture(mode);
        }
    return 0;
    
 }
int calibrate_skincolor()
    {
    
    Mat3b frame,framecr;
    namedWindow("SkinSelect", CV_WINDOW_AUTOSIZE);

    setMouseCallback("SkinSelect", CallBackFunc, NULL);
    if(!cap.isOpened()){
        cout << "Errore"; return -1;
        }

    Mat3b frameclone;
     frame = imread("scissors.jpg",1);
   // while(cap.read(frame)){
    while(1){
         
        frameclone = frame.clone();
        putText(frameclone,"Click on your hand",Point(0,200), FONT_HERSHEY_SIMPLEX,2.0f,Scalar(255,0,0));
        if(refreshFlag==1){
            refreshFlag = 0;
            
            cvtColor(frame, framecr, CV_BGR2HSV);
            cout<<"values"<<(int)framecr.at<Vec3b>(xvalue,yvalue)[0]<<","<<(int )framecr.at<Vec3b>(xvalue,yvalue)[1]<<","<<(int)framecr.at<Vec3b>(xvalue,yvalue)[2]<<endl;
            destroyWindow("SkinSelect");
            break;
            }
        imshow("SkinSelect",frameclone);
         waitKey(0);
        }
    return 1;
    }

int detect_gesture(char mode)
    {
   
          
        namedWindow("Threshold", CV_WINDOW_AUTOSIZE);
        namedWindow("Video", CV_WINDOW_AUTOSIZE);
   //     cvCreateTrackbar("min-brightness", "Video", &minV, 100, changevalhandl );
        if(!cap.isOpened()){
        cout << "Error"; return -1;
        }
        Mat3b frame;

        vector<vector<Point> > contours,contoursrock,contourspaper,contoursscissors;
        vector<Vec4i> hierarchy;
        Mat3b scissorframe = imread("Scissors.jpg",1);
        Mat3b paperframe = imread("Paper.jpg",1);
        Mat3b rockframe = imread("Rock.jpg",1);
        frame = imread("Scissors.jpg",1);
          float areascissors,arearock;
          
        /* Create contour for scissor template*/  
        contoursscissors = create_contours(scissorframe);
        int bigScissors = findBiggestContour(contoursscissors);
        
         Mat histBw = Mat::zeros(scissorframe.rows,scissorframe.cols,CV_8UC1);
         Mat histRockBw = Mat::zeros(rockframe.rows,rockframe.cols,CV_8UC1);
         drawContours(histBw,contoursscissors,bigScissors,Scalar(255),-1,8,hierarchy,0,Point());
         
          RotatedRect minRetscis;
          minRetscis = minAreaRect(Mat(contoursscissors[bigScissors]));
           float areascrect = minRetscis.size.height*minRetscis.size.width;
          
      
          Mat hist = createbwhist(histBw,&areascissors);
          cout<<"areascissors ratio:"<<areascissors/areascrect;
          
     
             /* Create contour for paper template*/  
        contourspaper = create_contours(paperframe);
        int bigpaper = findBiggestContour(contourspaper);
        
        
        
        contoursrock = create_contours(rockframe);
        int bigRock = findBiggestContour(contoursrock);
        
        
        
          drawContours(histRockBw,contoursrock,bigRock,Scalar(255),-1,8,hierarchy,0,Point());
          RotatedRect minRetRock ;
          minRetRock = minAreaRect(Mat(contoursrock[bigRock]));
          float arearockrect = minRetRock.size.height*minRetRock.size.width;
          
#ifdef debug
          imshow("maskrck",histRockBw);
#endif
          Mat histrck = createbwhist(histRockBw,&arearock);
          cout<<"arearock ratio:"<<arearock/arearockrect;
          
#ifdef debug
          imshow("histrck",histrck);
#endif
          destroyWindow("maskrck");
          destroyWindow("histrck");
          
          Mat histogramBW ;
          Mat drawing,m;
          
          
          
        while(cap.read(frame)){ 
            
            
        /* THRESHOLD ON HSV*/
         contours = create_contours(frame);
         int s = findBiggestContour(contours);
         
         drawing = Mat::zeros( frame.size(), CV_8UC1 );
         m = Mat(drawing.cols,drawing.rows,CV_32FC1);
         
         vector<Vec4i>  defects;
         convexHull(contours[s],m,CV_CLOCKWISE,0);
         
         vector<vector<Point> >hull(contours.size());
         convexHull(Mat(contours[s]),hull[0],false);
         drawContours( frame, hull, 0, Scalar(255), 1, 8, hierarchy, 0, Point() );
         
#ifdef debug
         cout<<"Rock:"<<matchShapes(contours[s],contoursrock[bigRock],1,0.0f)<<endl;
         cout<<"Paper:"<<matchShapes(contours[s],contourspaper[bigpaper],1,0.0f)<<endl;
         cout<<"Scissor:"<<matchShapes(contours[s],contoursscissors[bigScissors],1,0.0f)<<endl;
#endif
         if(mode == 'c'){
         /* contour matching*/
         if(matchShapes(contours[s],contoursscissors[bigScissors],1,0.0f)<0.3){
         putText(frame,"Scissors",Point(0,200), FONT_HERSHEY_SIMPLEX,2.0f,Scalar(255,0,0));
         //cout<<matchShapes(contours[s],contoursrock[bigRock],1,0.0f)<<endl;
             }
         
         else if(matchShapes(contours[s],contoursrock[bigRock],1,0.0f)<0.1){
             putText(frame,"Rock",Point(0,200), FONT_HERSHEY_SIMPLEX,2.0f,Scalar(0,0,255));
             }
         
         else if(matchShapes(contours[s],contourspaper[bigpaper],1,0.0f)<0.15){
             putText(frame,"Paper",Point(0,200), FONT_HERSHEY_SIMPLEX,2.0f,Scalar(255,0,255));
             }
             }
         
         
         if(mode == 'h'){
         /*histogram based recognition*/
//         
         histogramBW = Mat::zeros(frame.rows,frame.cols,CV_8UC1);        
         drawContours(histogramBW,contours,s,Scalar(255),-1,8,hierarchy,0,Point());
         float areainput;
         Mat histinput = createbwhist(histogramBW,&areainput);
         findContours( bw, contours, hierarchy, CV_RETR_TREE , CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );    
         imshow("input histogram",histinput);
         RotatedRect minRet ;
         minRet = minAreaRect(Mat(contours[s]));
         Point2f rect_points[4];
         minRet.points(rect_points);
        
         Size2f siz = minRet.size;
         float area = siz.height*siz.width;
         cout<< areainput/area<<endl;
             }
         // Hull defect count based recognition
         if(mode == 'H'){
             
             
          convexityDefects(contours[s],m,defects);
         
         cout<<"number of defects:"<<defects.size();
         
         int defectCount = 0;
         for( int k = 0 ;k< defects.size(); k++){
             //CvConvexityDefect* d=(CvConvexityDefect*)cvGetSeqElem(defect,k); 
             int startIdx = defects[k].val[0];
                int endIdx = defects[k].val[1];
                int defectPtIdx = defects[k].val[2];
                double depth = (double)defects[k].val[3]/256.0f; 
                
                int x =  contours[s][defectPtIdx].x;
                int y = contours[s][defectPtIdx].y;
                if(depth > 30){
               circle(frame,Point(x,y),10,Scalar(0,0,255),-1);
               defectCount++;
                    }
             }
         cout<<"defectcount :"<<defectCount<<endl;
           }
#ifdef Debug 
         imshow("Threshold",bw);
         imshow("drw", drawing);
         cout<<matchShapes(contours[s],contours[s],1,0);
#endif
         imshow("Video",frame);
         waitKey(5);
       }
            return 0;
    }


vector<vector<Point> >  create_contours(Mat3b frame )
    {
    
       vector<vector<Point> > contours;
        Mat3b framecr;
       vector<Vec4i> hierarchy;
        
        cvtColor(frame, framecr, CV_BGR2HSV); 
        //inRange(framecr,Scalar(0, 10, 60), Scalar(20, 50, 255), bw);
        
        //HSV color filter
       inRange(framecr,Scalar(0, 30, 60), Scalar(20, 150, 255), bw);
       
       //To remove holes of the contours
       dilate(bw, bw, Mat(), Point(1, 1), 2, 1, 1);
       erode(bw, bw, Mat(), Point(1, 1), 2, 1, 1);
       blur(bw,bw,Size(3,3));
       
        findContours( bw, contours, hierarchy, CV_RETR_TREE , CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );

        return contours;
    }

Mat createbwhist(Mat bw,float* area)
    {
    *area = 0.0f;
    Mat histogram = Mat::zeros(bw.rows,bw.cols,CV_8U);
    
    for(int i = 0;i<bw.cols;i++)
        {int hst_ht = bw.rows-1;
        for(int j=0 ;j<bw.rows;j++)
            {
            if(bw.at<uchar>(j,i) == 255){
                histogram.at<uchar>(hst_ht,i) = 255;
                hst_ht -- ;
                *area = *area+1;
                }
            }

        }
    return(histogram);
    
    }