"""
this is where i choose and extract features from my emails

"""

def message_features():
    """
        just a list of wanted features
    """
    return [
        'Dom',
        'Dow',
        'IsCalendarEvent',
        'IsInHTML',
        'InternalSenderId', # from CRM
        'InternalSenderPosition', # from CRM
        'ExternalSenderId', # from CRM
        'ClientId', # from CRM
        'SenderContactStatus', # data from CRM
        'SenderReceivesFinancialData', # data from CRM
        'NumberOfAttachments',
        'NumberOfWordAttachments',
        'NumberOfExcelAttachments',
        'NumberOfPdfAttachments',
        'NumberOfPptAttachments',
        'SenderTLD',
        'EstimatedLanguage',
        'Recepient1Id',
        'Recepient2Id',
        'Recepient3Id',
        'Recepient4Id',
        'Recepient5Id',
        'Recepient6Id',
        'Recepient7Id',
        'Recepient8Id',
        'CC1Id',
        'CC2Id',
        'CC3Id',
        'CC4Id',
        'CC5Id',
        'CC6Id',
        'CC7Id',
        'CC8Id',
        'BCCId',
        'IsForwarded',
        'NumberOfReplies',
        'IsReplyingToMe',
        'IAmInThread',
    ]
