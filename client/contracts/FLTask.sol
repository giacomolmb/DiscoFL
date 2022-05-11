// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract BCFLDraft {
    enum TaskStatus {    
        Pending,
        Initialized, 
        Running,
        Completed,
        Canceled
    }

    struct Worker {
        bool registered;
        uint8 workerId;
        uint16 latestScore;
    }

    struct SubmittedEval {
        address workerAddress;
        uint16[] scores; 
        //uint16 score; //only for testing
    }

    uint8 private numRounds;
    uint8 private round;
    uint8 public numWorkers = 0;
    mapping(address => Worker) private workers;
    mapping(uint8 => SubmittedEval[]) private roundScores;
    address public immutable requester;
    string private modelURI;
    TaskStatus public taskStatus;


    constructor() {
        requester = msg.sender;
        taskStatus = TaskStatus.Pending;
    }

    modifier onlyRequester() {
        require(msg.sender == requester, "This operation can be performed only by the task requester");
        _;
    }

    modifier onlyWorker() {
        require(workers[msg.sender].registered, "This operation can be performed only by the task workers");
        _;
    }

    modifier restrictAccess() {
        require((workers[msg.sender].registered || msg.sender == requester), "You do not have the rights to perform this operation");
        _;
    }

    modifier taskInitialized(){
        require(uint(taskStatus) == 1, "Task not initialized");
        _;
    }

    modifier taskRunning(){
        require(uint(taskStatus) == 2, "Task not running");
        _;
    }

    function initializeTask(string memory _modelURI, uint8 _numRounds) public payable onlyRequester{
        require(msg.value != 0, "Cannot initialize contract without deposit");
        modelURI = _modelURI;
        numRounds = _numRounds;
        taskStatus = TaskStatus.Initialized;
    }

    function startTask() public onlyRequester {
        taskStatus = TaskStatus.Running;
        round = 1;
    }

    function nextRound() public onlyRequester taskRunning {
        round++;
    }

    function getRound() public taskRunning view returns (uint8){
        return round;
    }

    function getDeposit() public onlyRequester view returns (uint) {
        return address(this).balance;
    }

    function getRequester() public view returns (address){
        return requester;
    }

    function getModelURI() public view restrictAccess returns (string memory){
        return modelURI;
    }

    function addWorker() public taskInitialized returns (string memory) {
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
