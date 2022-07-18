<h1 align="center">Fuzzy Utility Engine with Active Learning</h1>

![Overview](img/overview.png)

#### Abstract
Currently, we are consuming KYC information of our customers digitally, from walk-in customers and over phone calls. All these data populate in our pulse tool. However, it has been observed that the current system is not able to dedupe similar customers, which results in creating different personas for the same Individual. Other probable challenges were Inaccurate Insights, Untagged accounts, and Lack of integrity. To address this problem, I have created a fuzzy utility engine that can dedupe names based on various KYC information. The fuzzy algorithm works on a vector formed using the customer name and its feature set. Finally, to test the algorithm accuracy of the model, we initially went with manual testing. Subsequently, used that sample to automatedly annotate False positives using a classification model where we applied an active learning feedback approach to improving the model accuracy in real-time. 

I achieved an accuracy of 95% with a False positive rate of 5% and False negative rate of 0.2 from the baseline model where the algorithm ran on the single column. The baseline line model has an accuracy of 64% with greater than 30% false positive rate. Also, the active learning XGB classifier model achieves 98% accuracy.

#### Research
Initially, I thought the deduping problem would only contain spelling errors, for instance, Katya/katiyaa. However, after doing my research, considering that data is getting collected over calls and using physical platforms, I found many use cases of similarity between names. Some of the use cases I mentioned below:

The persona matching engine targeted 9 types of problems, which falls in the fuzzy matching realm.
1.	Textual Similarity (typos, etc.)
2.	Nickname (Mike/Michael)
3.	Missing spaces/hyphens (Mary Ellen/MaryEllen/Marry-Ellen)
4.	Initials (JE Smith/James Earl Smith)
5.	Out of order components (Diaz Carlos Alfonzo/Carlos Alfonzo Diaz)
6.  Name Split (First: Dick, Last: Van Dyke/First: Dick Van, Last: Dyke)
7.	Truncated Name (Charles Livingston/Charles Living)
8.	Missing Name (John Albert Lewis Lewis/John Lewis)
9.	Maiden name addition (or any other additional last name)

#### Future coverage
Two problems that we found of less importance for our system and can be covered in future are:
-   Name Swap (Bene Tyler/Tyler Bene)
-   Phonetics Similarity

#### Model Algorithm
The goal is to build a algorithm which can be scalable enough to run millions of records. Below are the building blocks of the algorithm

-   **Building a document term matrix**: As we have millions of records, and the algorithm has to run within a single spreadsheet, thus each record has to be compared with its adjacent entry. For instance, for every 100 k records, the calculation has to be made for $100^2$ k.
    Because of this reason, I went with matrix multiplication, a dynamic algorithmic approach to making a faster calculation.

-   **Applying TF-IDF**: The most common approach would be word count, but it will not be able to capture the word importance. Therefore, I decided to go with TF-IDF. It will multiply the number of times a term appears in a single document(Term Frequency) by the significance of the whole corpus. The more the word appears, the less valuable it becomes to differentiate documents from one another.

-   **N-Grams**: To make the TF-IDF more significant, I used N-grams to break the strings into smaller chunks. For our model, the n-gram of 3 is the right hyperparameter. After applying n-grams, I found significantly more overlap than the original string. 


![Model](img/model.png)

#### Testing and Active Learning

To make the entire use case more practical, I looked for cases where I can identify the matches and cases where there is close matches but are different names. These matches helps me to create more robust model. However, the sample was not availaible, I initially performed this step to create this data set. Below is an example:

<center>

|     Name       |   Fuzzy Output  | Type  | Label |
| -------------  |   ------------- | ----- | ----- |
|  Jeff Bezos    |   Jeff Bezos    | Match |   1   |
|  Jeif Bezzos   |   Jeff Bezos    | Match |   1   |
|  Andre Fernadez|   Andre Fernadez| close |   0   |
|  Andrai Feradez|   Andrai Feradez| close |   0   |

</center>

##### Building a model

Finally, I developed a classification model, where I tested the RandomForest classifier, SVM, and XGBoost Classifier. XGBoost performs well, with the highest precision, as our business goal is to have the least False positives.

However, I found that the model still produces incorrect labels for matches and close matches. To address this nondeterministic problem, I used a technique by which the model can be manually taught whether the labels are right or not, just like in a real-world situation. To achieve this, I used the concept of active learning. 


<center>

![alt-text-1](active_learning/active_learning/img/svm/svm_gt_without_normalization.png "title-1") ![alt-text-2](active_learning/active_learning/img/xgb/xgb_without_norm.png "title-2")

</center>

##### Pseudo Logic

I have used pool based labelling, where we select a sample from a pool of unlabelled data for labelling. The following pseudo algorithm represents the learning process, for pool-based sampling:
1. Divide the data to a ‘pool’ and a test-set
2. Select ‘k’ samples from the pool for the initial train-set and label them, the remaining data will be the validation-set
3. Normalize all the sets
4. Train the Model using the train-set, with balanced weights.
5. Use the trained model with the validation-set, get probabilities per sample.
6. Use the trained model with the test-set, get performance measures.
7. Select ‘k’ most-informative samples based on per-sample-probabilities, i.e., those that the model was most uncertain about regarding their labelling.
8. Move these ‘k’ samples from the validation set to the train-set and query their labels.
9. Inverse normalization for all the data-sets
10. Stop according to the stop criterion, otherwise go to 3.


