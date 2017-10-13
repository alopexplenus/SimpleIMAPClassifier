
# coding: utf-8

# In[82]:

from imaplib import IMAP4_SSL
from datetime import date,timedelta,datetime
from time import mktime
from time import strptime
import email
import dateutil.parser
from pylab import plot_date,show,xticks,date2num
from pylab import figure,hist,num2date
from matplotlib.dates import DateFormatter


# In[99]:

def getHeaders(imapAddress,address,password,folder,d):
 """ retrieve the headers of the emails 
     from d days ago until now """
 fulldata = []
 # imap connection
 mail = IMAP4_SSL(imapAddress)
 mail.login(address,password)
 print('selecting folder ', folder)
 typ = mail.select(folder)
 print('Response code:', typ)
 typ, data = mail.list()
 print('list():')
 print(data)
 print('retrieving the uids')
 interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
 result, data = mail.search(None,'(SENTSINCE {date})'.format(date=interval))
 print (len(data[0]),'Email numbers fetched.')
 print('retrieving the headers')
 for num in data[0].split():
    typ, mdata = mail.fetch(num, '(RFC822)')
    for response_part in mdata:
        if isinstance(response_part, tuple):
                part = response_part[1].decode('utf-8')
                msg = email.message_from_string(part)
                #print(msg.keys())
                #print(msg['Date'])

    fulldata.append(msg)
 print (len(fulldata),'headers fetched.')
 mail.close()
 mail.logout()
 return fulldata


# In[100]:

def diurnalPlot(headers):
 """ diurnal plot of the emails, 
     with years running along the x axis 
     and times of day on the y axis.
 """
 xday = []
 ytime = []
 for h in headers: 
  if len(h['Date']) > 1:
   #print('Message %s\n' % (h))
   #timestamp = mktime(dateutil.parser.parse(h))
   #mailstamp = datetime.fromtimestamp(timestamp)
   mailstamp = dateutil.parser.parse(h['Date'])
   xday.append(mailstamp)
   # Time the email is arrived
   # Note that years, month and day are not important here.
   y = datetime(2010,10,14, 
     mailstamp.hour, mailstamp.minute, mailstamp.second)
   ytime.append(y)
   #print("%s" % (mailstamp))
   #print("%s" % (y))

 plot_date(xday,ytime,'.',alpha=.7)
 xticks(rotation=30)
 return xday,ytime


# In[101]:

def dailyDistributioPlot(ytime):
 """ draw the histogram of the daily distribution """
 # converting dates to numbers
 numtime = [date2num(t) for t in ytime] 
 # plotting the histogram
 ax = figure().gca()
 _, _, patches = hist(numtime, bins=24,alpha=.5)
 # adding the labels for the x axis
 tks = [num2date(p.get_x()) for p in patches] 
 xticks(tks,rotation=75)
 # formatting the dates on the x axis
 ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))


# In[103]:

print('Fetching emails...')
headers = getHeaders('outlook.office365.com','semenov.nikita@interpont.com',
                      'Xe8Ag3kAdLSA','INBOX/notifs',1)
print(headers[0].keys())

print ('Plotting some statistics...')
xday,ytime = diurnalPlot(headers)
dailyDistributioPlot(ytime)
print (len(xday),'Emails analysed.')
show()


# In[ ]:




# In[ ]:



