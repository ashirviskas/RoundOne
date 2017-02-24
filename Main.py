import time

CACHE_SIZE = 100
SCORE_LOWERING_COEFFICIENT = 2
Caches = []

class Video:
    def __init__(self, size, id_, score = 0):
        self.size = size
        self.id_ = id_
        self.score = score

    def __str__(self):
        return str(self.size)+ " " + str(self.id)


class Endpoint:
    def __init__(self, latencyToData, id_ = None, caches = list(), latencies = {}, requests = list()):
        self.caches = caches
        self.latencies = latencies
        self.latencyToData = latencyToData
        self.requests = requests
        self.id_ = id_

    def __str__(self):
        return str(self.caches) + " " + str(self.latencies) + " Latency To Datacenter: " + str(self.latencyToData)

    def add_cache(self, cache, latency):
        self.caches.append(cache)
        self.latencies[cache.id_] = latency

    def getRequests(self, video_id):
        return self.requests[cache_id]
    def addRequests(self, request):
        self.requests.append(request)


class Request:
    def __init__(self, video_id, requests, endpoint = None):
        self.video_id = video_id
        self.requests = requests
        self.endpoint = endpoint

    def __str__(self):
        return str(self.video_id) + " " + str(self.requests) + " " + str(self.endpoint)


class Cache:
    def __init__(self, id_, size = CACHE_SIZE, videos = list(), endpoints= list()):
        self.videos = videos
        self.id_ = id_
        self.endpoints = endpoints
        self.size = size

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

    def add_video(self, video, max_score):
        lowest_score = max_score
        index = 0
        change = False
        if (not self.video_exists(video)):
            if len(self.videos)>0:
                for i in range(len(self.videos)):
                    if lowest_score > self.videos[i].score:
                        lowest_score = self.videos[i].score
                        index = i
                        change = True
                    else:
                        if self.free_space() >= video.size:
                            self.videos.append(video)
                            change = False
                            return
            if change:
                if (self.free_space()+ self.videos[index].size >= video.size):
                    self.videos[index] = video
                return True
        if len(self.videos) == 0:
            self.videos.append(video)

    def free_space(self):
        space = CACHE_SIZE
        for video in self.videos:
            space = space - video.size
        return int(space)
    def contains_endpoint(self, endpnt):
        for endpoint in self.endpoints:
            if endpoint.id_ == endpnt.id_:
                return True
        return False
def ParseFromFile(input_filename):
    start_time = time.time()
    file_object  = open(input_filename, "r")
    V, E, R, C, C_size = list(map(int, file_object.readline().split(' '))) #initialising things from data file
    CACHE_SIZE = int(C_size)
    lines = file_object.readlines()
    file_object.close()
    videos = lines[0].split(' ')
    Videos = []
    for i in range(len(videos)):
        Videos.append(Video(int(videos[i]),i))
    endpoints = []
    requests = []
    Caches = []
    current_line = 1
    for e in range(E):
        #print(lines[current_line])
        cache_num = 0
        latency_to_data, cache_num = lines[current_line].split(' ')
        endpoints.append(Endpoint(int(latency_to_data),e,[]))
        current_line +=1
        cache_num = int(cache_num.rstrip('\n'))
        for c in range(cache_num):
            cache_id, latency = lines[current_line].split(' ')
            current_line += 1
            latency = int(latency.rstrip('\n'))
            cache = Cache(int(cache_id))
            Caches.append(cache)
            endpoints[e].add_cache(cache, latency)
    for r in range(R):
        video_id, endpoint, request_num = lines[current_line].split(' ')
        current_line+=1
        request_num = int(request_num.rstrip('\n'))
        request = Request(int(video_id), int(request_num), int(endpoint))
        requests.append(request)

    Caches = CleanCacheList(Caches)
    AddRequestsToEndpoints(requests, endpoints)
    AddEndointsToCaches(endpoints, Caches)
    randomPlacement(Videos, Caches)
    Placement(Videos, Caches)
    file = open(input_filename+"answahs", "w")
    file.write(str(len(Caches)))
    for cache in Caches:
        file.write('\n')
        file.write(str(cache))
    file.close()


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
                temp = max_score - vid.score
                if temp > max_dif:
                    max_dif = temp
                    max_index_v = vid.id_
                    max_index_c = cache.id_
        if max_dif > 0:
             for cache in Caches:
                 if cache.id_ == max_index_c:
                    video.score = max_dif
                    cache.add_video(Video(video.size, video.id_, max_score), max_score)
                    video.score = 0
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
                    cache.add_video(Video(video.size,video.id_,max_score), max_score)
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
            newList.append(cache)
    return newList


def CountVideoScore(video, cache):
    score = 0
    score_to_lower = 0
    for endpoint in cache.endpoints:
        for request in endpoint.requests:
            if (video.id_ == request.video_id):
                score += (endpoint.latencyToData - endpoint.latencies[cache.id_])*request.requests
                for cache_two in Caches:
                    if cache_two.id_ != cache.id_:
                        if cache_two.video_exists(video):
                            score_to_lower = 1
    if (score_to_lower > 0):
        score = score / SCORE_LOWERING_COEFFICIENT

    return score





ParseFromFile("example.in")
ParseFromFile("me_at_the_zoo.in")
#ParseFromFile("trending_today.in")
#ParseFromFile("videos_worth_spreading.in")
#ParseFromFile("kittens.in")
