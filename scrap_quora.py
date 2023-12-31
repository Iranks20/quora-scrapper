from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests 
import csv

def get_number_answers(question_url=""):
    r = requests.get(question_url)
    if str(r.url).find('/unanswered') != -1:
        return 0, '0', ''
    soup = BeautifulSoup(r.text.encode('utf-8'), 'lxml')
    answer_count_elem = soup.find(class_='answer_count')
    
    if answer_count_elem:
        ans_num_st = answer_count_elem.text.split(' ')[0]
        ans_num = get_num(ans_num_st)
        return int(str(ans_num)), ans_num_st, soup
    else:
        # Handle the case where 'answer_count' element is not found
        return 0, '0', ''


def get_num(string_):
    num_st = ''
    for i in string_:
        if i.isdigit():
            num_st = num_st + i
    return num_st

def get_tags_of_question(soup):
    #r = requests.get(question_url)
    #soup = BeautifulSoup(page_source,'lxml')
    topic_elements = soup.find_all(class_ = 'TopicName')
    topics_ = [topic_element.text for topic_element in topic_elements]
    return topics_
    
def get_answers_of_question(soup,n_answer=4,question_url=''):
    #r = requests.get(question_url)
    #soup = BeautifulSoup(r.text.encode('utf-8'),'lxml')
    a = soup.find_all(class_='qu-wordBreak--break-word')
    try:
        answers = [a[i].text for i in range(n_answer)]
    except:
        print("Hellllllllllllllllllllllllllllllllllll"*3)
        print(question_url)
        soup = BeautifulSoup(requests.get(question_url).text.encode('utf-8'),'lxml')
        a = soup.find_all(class_='qu-wordBreak--break-word')
        answers = [a[i].text for i in range(n_answer)]
        
        return get_answers_of_question(soup)
    return answers
# ... (existing code remains the same)

def write_questions_from_this_topic(topic_url, row_writer, Exam_name='IPAD', max_q=50):
    SCROLL_PAUSE_TIME = 1
  
    driver = webdriver.Chrome()
    driver.get(topic_url)
    time.sleep(1)
    for i in range(70):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(.15)
        if i % 10 == 0:
            time.sleep(0.2)

    no_question_seen = 0
    no_question_useful = 0

    while no_question_useful < max_q:
        questions, question_links = get_qs_qlinks(driver.page_source)
        questions = questions[no_question_seen:]
        question_links = question_links[no_question_seen:]
        if len(questions) == 0:
            break
        print(len(questions))
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        for question, question_link in zip(questions, question_links):
            question_url = question_link
            print(question_url)
            no_question_seen += 1
            row_writer.writerow([Exam_name, question, question_url])  # Write question details to the CSV file
            no_question_useful += 1
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("At bottom of the page")
            break

    driver.close()                   
                   
    
# def get_qs_qlinks(page_source_):
#     soup = BeautifulSoup(page_source_, 'lxml')
#     a = soup.find_all(class_='Link___StyledBox-t2xg9c-0')
    
#     exclude_keywords = ['/profile/', '/topic/', 'about', 'careers', 'privacy', 'contact', 'languages', 'your_ad_choices', 'press']
    
#     qs = [x.text for x in a]
#     q_links = [x['href'] for x in a if not any(keyword in x['href'] for keyword in exclude_keywords)]
    
#     print(":: q_links ::", q_links)
#     return qs, q_links
def get_qs_qlinks(page_source_):
    soup = BeautifulSoup(page_source_, 'html.parser')
    question_links = soup.select('.q-box .Link___StyledBox-t2xg9c-0.dFkjrQ.qu-display--block.qu-cursor--pointer')  # Select the 'a' tag with the specific classes
    
    qs = [link.text for link in question_links]  # Extract text from the selected 'a' tag (question titles)
    q_links = [link['href'] for link in question_links]  # Extract the 'href' attribute from the selected 'a' tag (question URLs)
    
    print(":: Question Titles ::", qs)
    print(":: Question Links ::", q_links)
    return qs, q_links


def question_from_quora(base_url='https://www.quora.com/',topics=['What-Cool-Things-Can-One-Do-With-An-iPhone-And-iPad-That-Most-People-Dont-Know-About'],file_name="quora_questions.csv",Exam_name='IPAD'):
    url_for_topics = base_url + 'topic/'
    if file_name =="":
        file_name = topics[0]+"_questions.csv"
        
        
        
    file_handle = open(file_name,"w+",encoding='utf-8',errors='replace')
    row_writer = csv.writer(file_handle)

    header = ['Central Topic','Question','Question link','Tags on question','no of answers','Answer 1','Answer 2','Answer 3','Answer 4']
    row_writer.writerow(header)
    
    for topic in topics:
        print("Topic being extracted...")
        print(topic)
        print("==="*30)
        url = url_for_topics + topic
        write_questions_from_this_topic(url,row_writer,Exam_name)
        
    file_handle.close()


if __name__=='__main__':
    string_ = ['Instructions for user.','You will be asked for three inputs.','base_url : default set (need not to change)','topics   : topics mentioned on quora related to that exam : Please enter comma seperated topic names.','file_name: File name (csv file) in which the all data will be stored.','Exam_name: exam name i.e. IPAD or GRE,  to which exam given topics are related to. examples- IPAD or GRE']
    print("\n".join(string_))
    print("==="*40)
    print("default values are below....")
    print("""base_url='https://www.quora.com/',topics=['What-Cool-Things-Can-One-Do-With-An-iPhone-And-iPad-That-Most-People-Dont-Know-About'],file_name="quora_questions.csv",Exam_name='IPAD'""")
    print("==="*40)

    base_url = 'https://www.quora.com/'
    
    print("Enter the topic names as mentioned on quora.\nexample\nWhat-Cool-Things-Can-One-Do-With-An-iPhone-And-iPad-That-Most-People-Dont-Know-About,What-Cool-Things-Can-One-Do-With-An-iPhone-And-iPad-That-Most-People-Dont-Know-About-2018\n\nif do not want to change press enter\n")
    
    temp = ""
    
    temp = input("....."*20+'\n')
    if len(temp)<2:
        topics = ['What-Cool-Things-Can-One-Do-With-An-iPhone-And-iPad-That-Most-People-Dont-Know-About']
        print('topics set to default value')
    else:
        topics = temp.replace(' ','').split(",")
    print("Enter the file name in which data will be stored. examples\nquora_questions.csv\npress enter for default value\n")
    temp = ''
    temp = input("....."*20+'\n')
    if len(temp)<2:
        file_name = 'quora_questions.csv'
    else:
        file_name = temp
    print("Enter the central topic name.\nexample\nIPAD\npress enter for default value.")
    temp = ""
    temp = input("....."*20+'\n')
    if len(temp)<2:
        Exam_name = 'IPAD'
    else:
        Exam_name = temp
    print("....."*20,'\nThese are inputs\n')
    print(base_url)
    print(topics)
    print(file_name)
    print(Exam_name)
    input("....."*20+"\nPress enter to continue")
    
    question_from_quora(base_url,topics,file_name,Exam_name)
    print("\a\a\a\a")
#question_from_quora()