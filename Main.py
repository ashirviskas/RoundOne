import time
import operator


CACHE_SIZE = 100
SCORE_LOWERING_COEFFICIENT = 2
Caches = []
COUNTER_MAX = 45
SIZE_SCORE_MULTI = 50
ENDPOINT_SCORES_ENABLED = True

class Video:
    def __init__(self, size, id_, scores = {}, nodestimes = {}):
        self.size = size
        self.id_ = id_
        self.scores = {}
        self.endpointstimes = {}


    def __str__(self):
        return str(self.size)+ " " + str(self.id)


class Endpoint:
    def __init__(self, latencyToData, id_ = None, caches = list(), requests = list()):
        self.caches = caches
        self.latencies = {}
        self.latencyToData = latencyToData
        self.requests = []
        self.id_ = id_

    def __str__(self):
        return str(self.caches) + " " + str(self.latencies) + " Latency To Datacenter: " + str(self.latencyToData)

    def add_cache(self, cache, latency):
        self.caches.append(cache)
        self.latencies[cache.id_] = latency

    def getRequests(self, video_id):
        reqs = []
        for r in self.requests:
            if r.video_id == video_id:
                reqs.append(r)
        return reqs
    def addRequests(self, request):
        if (request.endpoint == self.id_):
            self.requests.append(request)


class Request:
    def __init__(self, video_id, requests, endpoint = None):
        self.video_id = video_id
        self.requests = requests
        self.endpoint = endpoint

    def __str__(self):
        return str(self.video_id) + " " + str(self.requests) + " " + str(self.endpoint)


class Cache:
    def __init__(self, id_, size = CACHE_SIZE, endpoints= list(), min_score = 0,min_score_id = 0):
        self.videos = []
        self.id_ = id_
        self.endpoints = []
        self.size = size
        self.min_score = min_score
        self.min_score_id = min_score_id
        self.free_space_left = size

    def __str__(self):
        string = str(self.id_)
        for video in self.videos:
            string = string + " " + str(video.id_)
        return string

    def video_exists(self, video):
        for vid in self.videos:
            if vid.id_ == video.id_:
                return True
        return False
    def find_mins(self):
        for i in range(len(self.videos)):
            if self.videos[i].scores[self.id_] < self.min_score:
                self.min_score = self.videos[i].scores[self.id_]
                self.min_score_id = i

    def add_video(self, video, score):
        change = False
        index = 0
        vid = Video(video.size,video.id_,video.scores)
        video_size = video.size
        if self.free_space_left >= video_size:
            if len(self.videos) == 0:
                self.videos.append(vid)
                #self.free_space()
                self.min_score = score
                self.min_score_id = 0
                return
        if (not self.video_exists(video)):
            if len(self.videos)>0:
                if self.free_space_left >= video_size:
                    self.videos.append(vid)
                    #self.free_space()
                    return
                elif score > self.min_score:
                    if self.free_space_left + self.videos[self.min_score_id].size >= video_size:
                        self.videos[self.min_score_id] = vid
                        self.min_score = score
                        #self.free_space()
                        return
                    else:
                        most_worth_id = 0
                        most_worth_score = 0
                        for i in range(len(self.videos)):
                            if self.free_space_left + self.videos[i].size >= video_size:
                                score_vid = self.videos[i].scores[self.id_]
                                if score > score_vid or (score == score_vid and self.free_space_left + self.videos[i].size < video.size):
                                    scoreV = score_vid + (self.free_space_left + self.videos[i].size - video.size)*SIZE_SCORE_MULTI
                                    if (scoreV > most_worth_score):
                                        most_worth_score = scoreV
                                        most_worth_id = i
                        if (most_worth_score > 0):
                            self.videos[most_worth_id] = vid
                            #self.free_space()
                            return

    def free_space(self):
        space = CACHE_SIZE
        for video in self.videos:
            space = space - video.size
        self.free_space_left = space
        return int(space)
    def contains_endpoint(self, endpnt):
        for endpoint in self.endpoints:
            if endpoint.id_ == endpnt.id_:
                return True
        return False


def ParseFromFile(input_filename):
    start_time = time.time()
    print("Starting To work with", input_filename)
    file_object  = open(input_filename, "r")
    V, E, R, C, C_size = list(map(int, file_object.readline().split(' '))) #initialising things from data file
    CACHE_SIZE = int(C_size)
    lines = file_object.readlines()
    file_object.close()
    videos_temp = lines[0].split(' ')
    Videos = []
    for i in range(len(videos_temp)):
        Videos.append(Video(int(videos_temp[i].rstrip('\n')),i))
    Endpoints = []
    requests = []
    Ch = []
    current_line = 1
    for e in range(E):
        #print(lines[current_line])
        cache_num = 0
        latency_to_data, cache_num = lines[current_line].split(' ')
        Endpoints.append(Endpoint(int(latency_to_data),e,[]))
        current_line +=1
        cache_num = int(cache_num.rstrip('\n'))
        for c in range(cache_num):
            cache_id, latency = lines[current_line].split(' ')
            current_line += 1
            latency = int(latency.rstrip('\n'))
            Ch.append(Cache(int(cache_id)))
            Endpoints[e].add_cache(Ch[len(Ch)-1], latency)
    for r in range(R):
        video_id, endpoint, request_num = lines[current_line].split(' ')
        current_line+=1
        request_num = int(request_num.rstrip('\n'))
        request = Request(int(video_id), int(request_num), int(endpoint))
        requests.append(request)

    Caches = CleanCacheList(Ch)
    #MaxScoresForVideos(Videos, Caches)
    AddRequestsToEndpoints(requests, Endpoints)
    AddEndointsToCaches(Endpoints, Caches)
    MaxScoresForVideos(Videos, Caches) # also adds endpoint latencies
    algorithm_time = time.time()
    PlacementNew(Videos, Caches)
    print("Running Time PlacementNew: ", time.time() - algorithm_time)

    file = open(input_filename+"answahs", "w")
    for e in Endpoints:
        print("Endpoints ",e.id_," Requests:")
        for r in e.requests:
            print(r)
    file.write(str(len(Caches)))
    for cache in Caches:
        file.write('\n')
        file.write(str(cache))
    file.close()
    print("Running Time: ", time.time() - start_time)


def MaxScoresForVideos(Videos, Caches):
    print("Getting MaxScores for Videos")
    for video in Videos:
        for cache in Caches:
            score = CountVideoScore(video, cache)
            video.scores[cache.id_] = score
            if (ENDPOINT_SCORES_ENABLED):
                for endpoint in cache.endpoints: # NEEEEDS IFFF!!
                    for r in endpoint.getRequests(video.id_):
                        if video.id_== r.video_id:
                            video.endpointstimes[endpoint.id_]=endpoint.latencies[cache.id_]
    print("Dese Stuffs Finished")



    #for video in Videos:
        #print ("Video: ",video.id_, " Scores: ", video.scores)


def PlacementNew(Videos, Caches):

    for video in Videos:
        counter = 0
        for cache in Caches:
            if (counter < COUNTER_MAX):
                score = video.scores[cache.id_]
                if (score>0):
                    cache.add_video(video,score)
                    cache.free_space()
            else:
                break



def Placement(Videos, Caches):
    max_index_v = 5

    for video in Videos:
        max_dif = 0
        max_score = 0
        max_index_c = 0
        max_index_v = 0
        for cache in Caches:
            max_score = CountVideoScore(video, cache)
            for vid in cache.videos:
                temp = max_score - vid.scores[cache.id_]
                if temp > max_dif:
                    max_dif = temp
                    max_index_v = vid.id_
                    max_index_c = cache.id_
        if max_dif > 0:
             for cache in Caches:
                 if cache.id_ == max_index_c:
                    video.scores[cache.id_] = max_score
                    cache.add_video(video, max_score)
                    break
    return


def randomPlacement(Videos, Caches):
    max_index_v = 5
    for video in Videos:
        max_score = 0
        max_index_c = 0
        max_index_v = 0
        for cache in Caches:
            S = CountVideoScore(video, cache)
            if S > max_score:
                max_score = S
                max_index_v = video.id_
                max_index_c = cache.id_
        if max_score > 0:
             for cache in Caches:
                 if cache.id_ == max_index_c:
                    video.scores[cache.id_] = max_score
                    cache.add_video(video, max_score)
                    return
    return

def AddEndointsToCaches(Endpoints, Caches):
    for cachee in Caches:
        for endpoint in Endpoints:
            for cache in endpoint.caches:
                if cache.id_ == cachee.id_:
                    if (not cachee.contains_endpoint(endpoint)):
                        cachee.endpoints.append(endpoint)

def AddRequestsToEndpoints(Requests, Endpoints):
    for i in range(len(Endpoints)):
        for request in Requests:
            if i == int(request.endpoint):
                Endpoints[i].addRequests(request)




def CleanCacheList(Caches):
    newList = []
    for cache in Caches:
        exists = False
        for element in newList:
            if cache.id_ == element.id_:
                exists = True
        if(not exists):
            newList.append(Cache(cache.id_))
    return newList


def CountVideoScore(video, cache):
    score = 0
    for endpoint in cache.endpoints:
        for request in endpoint.requests:
            if (video.id_ == request.video_id):
                score += (endpoint.latencyToData - endpoint.latencies[cache.id_])*request.requests
    return score





ParseFromFile("example.in")
#ParseFromFile("me_at_the_zoo.in")
#ParseFromFile("videos_worth_spreading.in")
#ParseFromFile("trending_today.in")
#ParseFromFile("kittens.in")
