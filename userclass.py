class user:
    def __init__(self,chat_id):
        self.segments = []
        self.chat_id = chat_id
    def addSegments(self,list):
        for i in list:
            self.segments.append(i)
        
