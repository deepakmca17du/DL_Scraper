import requests
from lxml import html
import pytesseract
import json
from urllib.parse import urlparse
flag = 0

def get_captcha(captcha):
    pass

def fill_form(dl,dob):
    global flag
    while(flag==0):
        #starting a new session
        session_requests = requests.session()

        url = 'https://parivahan.gov.in/rcdlstatus/?pur_cd=101'

        #get webpage data from server
        res = session_requests.get(url)

        #converting to html element
        tree = html.document_fromstring(res.content)
        #source of captcha image
        image_src = 'https://parivahan.gov.in'+str(tree.xpath('/img[@id="form_rcdl:j_idt37:j_idt43"]/@src'))

        captcha = session_requests.get(image_src)
        with open("captcha_image.png",'wb') as f:
            f.write(captcha.content)

        #converting captcha to gray scale and then to string
        gray = captcha.convert('L')
        gray.save('captcha_gray.png')
        bw = gray.point(lambda x: 0 if x<1 else 255,'1')
        bw.save('captcha_thresholded.png')
        pytesseract.image_to_string(bw)

        #necessary form data to be filled
        form_data = {
            'form_rcdl:tf_dlNO' : dl,
            'form_rcdl:tf_dob_input' :  dob,
            'form_rcdl:j_idt38:CaptchaID' : bw,
            'form_rcdl:j_idt50' : 'form_rcdl:j_idt50',
        }

        #posting form data
        response = session_requests.post('https://parivahan.gov.in/rcdlstatus/vahan/rcDlHome.xhtml', data = form_data)

        result = html.document_fromstring(response.content)

        if len(result.xpath('//*[@id="form_rcdl:j_idt19"]/div/ul/li/span[1]/text()')) !=0 :
            print("Error while submitting captcha. Retrying...")
            continue

        if(len(result.xpath('//*[@id="form_rcdl:j_idt127"]' + '/div[1]/text()')) == 0) :
            print("Wrong details filled! Terminating...")
            break

        table_content = '//*[@id="form_rcdl:j_idt127"]'
        table2_content = '//*[@id="form_rcdl:j_idt174"]'

        current_status = result.xpath(table_content + '/table[1]/tr[1]/td[2]')[0].text_content()
        holder_name = result.xpath(table_content + '/table[1]/tr[2]/td[2]')[0].text_content()
        doi = result.xpath(table_content + '/table[1]/tr[3]/td[2]')[0].text_content()
        last_trans = result.xpath(table_content + '/table[1]/tr[4]/td[2]')[0].text_content()
        dl_no = result.xpath(table_content + '/table[1]/tr[5]/td[2]')[0].text_content()
        non_trans_from = result.xpath(table_content + '/table[2]/tr[1]/td[2]')[0].text_content()
        non_trans_to = result.xpath(table_content + '/table[2]/tr[1]/td[3]')[0].text_content()
        trans_from = result.xpath(table_content + '/table[2]/tr[2]/td[2]')[0].text_content()
        trans_to = result.xpath(table_content + '/table[2]/tr[2]/td[3]')[0].text_content()
        hazard_valid = result.xpath(table_content + '/table[3]/tr/td[2]')[0].text_content()
        hill_valid = result.xpath(table_content + '/table[3]/tr/td[4]')[0].text_content()
        cov = result.xpath(table2_content + '/td[1]')[0].text_content()
        class_veh = result.xpath(table2_content + '/td[2]')[0].text_content()
        cov_date = result.xpath(table2_content + '/td[3]')[0].text_content()

        display_items = {

            "Current Status": current_status,

            "Holder's Name": holder_name,

            "Date Of Issue": doi,

            "Last Transaction At": last_trans,

            "Old / New DL No.": dl_no,

            "NON-TRANSPORT Valid From": non_trans_from,

            "NON-TRANSPORT Valid Till": non_trans_to,

            "TRANSPORT Valid From": trans_from,

            "TRANSPORT Valid Till": trans_to,

            "HAZARD Valid Till": hazard_valid,

            "HILL Valid Till": hill_valid,

            "COV Category": cov,

            "Class Of Vehicle": class_veh,

            "COV Date Of Issue": cov_date

        }

        with open("Display_details.json", "w") as f:
            json.dump(display_items, f)

        print("Required Details stored sucessfully...")
        flag = 1


if __name__ == '__main__':
    dl = input("Enter the driving license no in the format (SS-RRYYYYNNNNNNN) :")
    dob = input ("Enter your date of birth in the format(dd-mm-yyyy) :")
    fill_form(dl,dob)