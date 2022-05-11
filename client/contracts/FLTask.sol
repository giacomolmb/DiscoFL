// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

// Smart contract representing a FL task
contract FLTask {
    // Representing the status of the task
    // Pending: invalid status, created when the smart contract is deployed
    // Initialized: the task is ready to be joined by workers
    // Running, Completed, Canceled: self-explanatory
    enum TaskStatus {    
        Pending, 
        Initialized, 
        Running,
        Completed,
        Canceled
    }

    //Struct representing a wokrer of the task, still under development
    //the boolean field is used to verify that a worker cannot join the task twice
    struct Worker {
        bool registered;
        uint8 workerId;
        uint16 latestScore;
    }

    //struct representing the evaluation submitted by a worker at the end of the evaluation phase
    struct SubmittedEval {
        address workerAddress;
        uint16[] scores; 
        //uint16 score; //only for testing
    }

    
    uint8 private numRounds; //number of rounds of the fl task
    uint8 private round; //number of the actual round
    uint8 public numWorkers = 0;
    mapping(address => Worker) private workers; //to each worker address is associated his worker object
    mapping(uint8 => SubmittedEval[]) private roundScores;//to each round are associated the submitted evaluations
    address public immutable requester;
    string private modelURI; //URI of the model pushed by the requester at initialization phase
    TaskStatus public taskStatus;

    constructor() {
        requester = msg.sender;
        taskStatus = TaskStatus.Pending;
    }

    // function modifier allowing the function to be called only by the requester
    modifier onlyRequester() {
        require(msg.sender == requester, "This operation can be performed only by the task requester");
        _;
    }

    // function modifier allowing the function to be called only by the workers
    modifier onlyWorker() {
        require(workers[msg.sender].registered, "This operation can be performed only by the task workers");
        _;
    }

    // function modifier allowing the function to be called only by requester and workers
    modifier restrictAccess() {
        require((workers[msg.sender].registered || msg.sender == requester), "You do not have the rights to perform this operation");
        _;
    }

    // function modifier allowing the function to be called only if the task has been initialized
    modifier taskInitialized(){
        require(uint(taskStatus) == 1, "Task not initialized");
        _;
    }

    // function modifier allowing the function to be called only if the task has started
    modifier taskRunning(){
        require(uint(taskStatus) == 2, "Task not running");
        _;
    }

    // function called to initialize the task, mandatory to put a deposit in the smart contract
    function initializeTask(string memory _modelURI, uint8 _numRounds) public payable onlyRequester{
        require(msg.value != 0, "Cannot initialize contract without deposit");
        modelURI = _modelURI;
        numRounds = _numRounds;
        taskStatus = TaskStatus.Initialized;
    }

    // start the task
    function startTask() public onlyRequester {
        taskStatus = TaskStatus.Running;
        round = 1;
    }

    // advance round
    function nextRound() public onlyRequester taskRunning {
        round++;
    }

    // get the number of actual round
    function getRound() public taskRunning view returns (uint8){
        return round;
    }

    // get the amount of money deposited in the smart contract
    function getDeposit() public onlyRequester view returns (uint) {
        return address(this).balance;
    }

    // get the address of the requester
    function getRequester() public view returns (address){
        return requester;
    }

    // get the URI of the model
    function getModelURI() public view restrictAccess returns (string memory){
        return modelURI;
    }

    function joinTask() public taskInitialized returns (string memory) {
        require(!workers[msg.sender].registered, "Worker is already registered");
        require(msg.sender != requester, "Requester cannot be a worker!");
        Worker memory worker;
        worker.registered = true;
        worker.workerId = numWorkers + 1;
        workers[msg.sender] = worker;
        numWorkers++;
        return modelURI;
    }

    function removeWorker() public {
        delete workers[msg.sender];
        numWorkers--;
    }

    function submitScore(uint16[] memory _scores) public onlyWorker taskRunning {
        roundScores[round].push(SubmittedEval({
            workerAddress: msg.sender,
            scores: _scores
        }));
    }

    function getSubmissionsNumber() public onlyRequester view returns (uint8){
        return uint8(roundScores[round].length);
    }

    function getSubmissions() public onlyRequester taskRunning view returns (SubmittedEval[] memory) {
        SubmittedEval[] memory evals = new SubmittedEval[](getSubmissionsNumber());
        for (uint8 i = 0; i < roundScores[round].length; i++){
            evals[i] = roundScores[round][i];
        }
        return evals;
    }
}
