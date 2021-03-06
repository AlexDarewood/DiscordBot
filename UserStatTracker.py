class UserStatTracker:

    userStats = {}

    def __init__(self, users, auditLines):
        for user in users:
            self.userStats[user] = 0

        lines = auditLines

        for line in lines:
            splitLine = line.split(',')
            name = splitLine[0][0:-5]
            self.userStats[name] += 1


    def getStats(self):
        return {k:v for k,v in self.userStats.items() if v > 10}

    def updateStats(self, user):
        tUser = user[0:-5]
        print("Logging " + user + " as " + tUser)
        self.userStats.setdefault(tUser)

        if self.userStats[tUser] == None:
            self.userStats[tUser] = 1
        else:
            self.userStats[tUser] += 1
        return 0

        
    
        
    

    