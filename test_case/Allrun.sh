#echo "-> Running makeMesh on a single processor"
#./makeMesh 1 

#echo "-> Running openFlowBattery"
#openFlowBattery &> solver.log 

#echo "-> Running sample_negative_electrode"
#postProcess -func sample_negative_electrode -latestTime -region negative_electrode &> sample_negative_electrode.log

#echo "-> Running sample_positive_electrode"
#postProcess -func sample_positive_electrode -latestTime -region positive_electrode &> sample_positive_electrode.log

#echo "-> Plotting data"
#QT_LOGGING_RULES="*.warning=false" python3 plotMidHeightLine.py 

