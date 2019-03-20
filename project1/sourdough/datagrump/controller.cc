#include <iostream>

#include "controller.hh"
#include "timestamp.hh"
#include "windowsize.hh"
using namespace std;

#define TARGET 55
#define INTERVAL 40
/* Default constructor */
Controller::Controller( const bool debug )
  : debug_( debug ),
  	windowsize_ (1),// start with a window size of 1
  	//ssthresh_(1)
  	state_(0), // slowstart 0, congest-avoidance 1
  	dup_ack_counter_(0),
  	dup_ack_(0),
  	first_time_(false),
  	num_backoffs_(1),
  	next_time_(0),
  	ssthresh_(100),
  	first_timeout_(false)
{ 
	
	
}

/* Get current window size, in datagrams */
unsigned int Controller::window_size()
{

  unsigned int the_window_size = windowsize_;
  
  if ( debug_ ) {
    cerr << "At time " << timestamp_ms()
	 << " window size is " << the_window_size << endl;
  }

  return the_window_size;
}

/* A datagram was sent */
void Controller::datagram_was_sent( const uint64_t sequence_number,
				    /* of the sent datagram */
				    const uint64_t send_timestamp,
                                    /* in milliseconds */
				    const bool after_timeout
				    /* datagram was sent because of a timeout */ )
{
  /* Default: take no action */

  if ( debug_ ) {
    cerr << "At time " << send_timestamp
	 << " sent datagram " << sequence_number << " (timeout = " << after_timeout << ")\n";
  }
  if (after_timeout == true){
  	/* window size back to 1	*/
  	//windowsize_ = 1;
  	if (first_timeout_==false){
  		first_timeout_ = true;
  		cout <<"windowsize_ at first time out:"
  		<<windowsize_<<endl;
  	}
  	
  	ssthresh_ = windowsize_/2;
  	windowsize_ = 1;
  	//state_ = 0; // back to slow start 
  	//cout << "Timeout: reduce window size to 1" << windowsize_;

  }

  else if (windowsize_ < ssthresh_ ){
  	//windowsize_ = std::min(windowsize_+1, (unsigned int)12);
  	// windowsize_ = std::min(windowsize_ +1, (unsigned int)10);
  	windowsize_ = windowsize_+1;
  	//cout << "Normal additive increase: window size to " << windowsize_;
  }
  else if (windowsize_ >= ssthresh_ ){
  	windowsize_ += 1/windowsize_;
  }
  // else if (state_ == 1){
  // 	cout<<"congestion avoidance phase" <<windowsize_; 
  // 	windowsize_ = std::min(windowsize_ + 1/windowsize_, (unsigned int)10);
  // }
}

/* An ack was received */
void Controller::ack_received( const uint64_t sequence_number_acked,
			       /* what sequence number was acknowledged */
			       const uint64_t send_timestamp_acked,
			       /* when the acknowledged datagram was sent (sender's clock) */
			       const uint64_t recv_timestamp_acked,
			       /* when the acknowledged datagram was received (receiver's clock)*/
			       const uint64_t timestamp_ack_received )
                               /* when the ack was received (by sender) */
{
  /* Default: take no action */
  if (dup_ack_ != sequence_number_acked){
  	dup_ack_counter_ = 0;
  	dup_ack_ = sequence_number_acked;
  	// cout<<"dup_ack_:"<<dup_ack_<<"sequence_number_acked:"
  	// <<sequence_number_acked<<endl;
  }
  else{
  	dup_ack_counter_ += 1;
  	cout<<"Duplicate ack counter increment"<<endl;
  }

  if (dup_ack_counter_ == 2){
  	//enter congestion avoidance phase
  	cout << "Congestion Avoidance phase, windowsize_" << windowsize_<<windowsize_/2;
  	state_ = 1;

  	windowsize_ /= 2;
  	dup_ack_counter_ = 0;
  }

  uint64_t current_rtt = timestamp_ack_received - send_timestamp_acked;
  // cout<<"ack received timestamp:"<<timestamp_ack_received
  // <<"send time:"<<send_timestamp_acked <<endl;
  // cout<<"current rtt:"<<current_rtt<<endl;

  uint64_t current_time = timestamp_ms();
  // cout<<"current_time:"<<current_time<<endl;

  if ( current_rtt<TARGET ){
  	windowsize_ += TARGET/current_rtt;
  	first_time_ = true;
  	num_backoffs_ = 1;

  }
  else if ( first_time_== true ){
  	next_time_ = current_time + INTERVAL;
  	first_time_ = false;
  }
  else if ( current_time > next_time_){
  	next_time_ = current_time + INTERVAL/num_backoffs_;
  	num_backoffs_ +=1;
  	ssthresh_ = windowsize_/2;
  	windowsize_ = 8; // set it to the window size from last timeout??
  }
  if ( debug_ ) {
    cerr << "At time " << timestamp_ack_received
	 << " received ack for datagram " << sequence_number_acked
	 << " (send @ time " << send_timestamp_acked
	 << ", received @ time " << recv_timestamp_acked << " by receiver's clock)"
	 << endl;
  }
}

/* How long to wait (in milliseconds) if there are no acks
   before sending one more datagram */
unsigned int Controller::timeout_ms()
{
  return 100; /* timeout of one second */
}
