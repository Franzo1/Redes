
class CongestionControl:

    def __init__(self, MSS: int):
        
        self.current_state = "slow start"
        self.MSS = MSS
        self.cwnd = MSS
        self.ssthresh = None
        self.firstTimeout = True
    
    def set_current_state(self, current_state):
        self.current_state = current_state
    
    def set_cwnd(self, cwnd):
        self.cwnd = cwnd
    
    def set_ssthresh(self, ssthresh):
        self.ssthresh = ssthresh

    def get_current_state(self):
        return self.current_state

    def get_cwnd(self):
        return self.cwnd
    
    def get_ssthresh(self):
        return self.ssthresh

    def get_MSS_in_cwnd(self):
        return self.cwnd//self.MSS
    
    def event_ack_received(self):
        if self.current_state == "slow start":
            self.cwnd += self.MSS
            if self.get_ssthresh() != None:
                if self.get_cwnd() >= self.get_ssthresh():
                    self.set_current_state("congestion avoidance")
            return
        if self.current_state == "congestion avoidance":
            self.cwnd += self.MSS/self.get_MSS_in_cwnd()
            return
    
    def event_timeout(self):
        if self.firstTimeout == True and self.get_current_state() == "slow start":
            self.firstTimeout = False
        if self.get_current_state() == "congestion avoidance":
            self.set_current_state("slow start")
        self.set_ssthresh(self.get_cwnd()//2)
        self.set_cwnd(self.MSS)

    def is_state_slow_start(self):
        if self.get_current_state() == "slow start":
            return True
        else:
            return False
        
    def is_state_congestion_avoidance(self):
        if self.get_current_state() == "congestion avoidance":
            return True
        else:
            return False