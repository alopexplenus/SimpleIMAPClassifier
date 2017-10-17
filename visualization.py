"""
Here the plotting functions go
"""
import email
from datetime import  datetime
import dateutil.parser
from matplotlib.dates import DateFormatter
from pylab import plot_date, show, xticks, date2num
from pylab import figure, hist, num2date

def diurnalplot(headers):
    """ diurnal plot of the emails,
        with years running along the x axis
        and times of day on the y axis.
    """
    xday = []
    ytime = []
    for header in headers:
        print(header['Date'], header['From'], email.header.decode_header(header['Subject']))
        if len(header['Date']) > 1:
            #print('Message %s\n' % (h))
            #timestamp = mktime(dateutil.parser.parse(h))
            #mailstamp = datetime.fromtimestamp(timestamp)
            mailstamp = dateutil.parser.parse(header['Date'])
            xday.append(mailstamp)
            # Time the email is arrived
            # Note that years, month and day are not important here.
            y = datetime(2010, 10, 14, mailstamp.hour, mailstamp.minute, mailstamp.second)
            ytime.append(y)
            #print("%s" % (mailstamp))
            #print("%s" % (y))

    plot_date(xday, ytime, '.', alpha=.7)
    xticks(rotation=30)
    return xday, ytime


def dailyDistributioPlot(ytime):
    """ draw the histogram of the daily distribution """
    # converting dates to numbers
    numtime = [date2num(t) for t in ytime]
    # plotting the histogram
    ax = figure().gca()
    _, _, patches = hist(numtime, bins=24, alpha=.5)
    # adding the labels for the x axis
    tks = [num2date(p.get_x()) for p in patches]
    xticks(tks, rotation=75)
    # formatting the dates on the x axis
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))


