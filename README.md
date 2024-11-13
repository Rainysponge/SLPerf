# SLPerf


## Tree
   
SLFrame  
      │  config.yaml  
      │  dataTest.py  
      │  log.txt  
      │  Test.py  # main
      │            
      ├─core  
      │  │  splitApi.py  
      │  │  splitApiO.py  
      │  │           
      │  ├─communication  
      │  │  │  base_com_manager.py  
      │  │  │  message.py  
      │  │  │  msg_manager.py  
      │  │  │  observer.py  
      │  │  │  __init__.py  
      │  │  │    
      │  │  ├─mpi  
      │  │  │  │  mpi_com_mananger.py  
      │  │  │  │  mpi_receive_thread.py  
      │  │  │  │  mpi_send_thread.py  
      │  │  │  │  __init__.py  
      │  │    
      │  │            
      │  ├─dataset …… 
      │  │  │  abstractDataset.py  
      │  │  │  abstractDatasetFactory.py  
      │  │  │  baseDataset.py  
      │  │  │  baseDatasetFactory.py  
      │  │  │  datasetFactory.py  
      │  │  │    
      │  │  ├─controller  
      │  │  │  │  adultController.py  
      │  │  │  │  cheXpertController.py  
      │  │  │  │  cifar10Controller.py  
      │  │  │  │  fashionmnistController.py  
      │  │  │  │  germanController.py  
      │  │  │  │  mnistController.py  
      │  │  │    
      │  │  │            
      │  │  ├─dataset  
      │  │  │  │  adult.py  
      │  │  │  │  cheXpert.py  
      │  │  │  │  cifar10.py  
      │  │  │  │  fashionmnist.py  
      │  │  │  │  german.py  
      │  │  │  │  mnist.py  
      │  │  │            
      │  │  ├─partition 
      │  │  │  │  basePartition.py  
      │  │  │  │  basePartitionFactory.py  
      │  │  │  │  cifar10Partition.py  
      │  │  │  │  partitionFactory.py  
      │  │  │  │  partitionUtils.py  
      │  │          
      │  ├─log  
      │  │  │  abstractLog.py  
      │  │  │  baseLog.py  
      │  │  │  Log.py  
      │  │    
      │  │            
      │  ├─model  
      │  │  │  Alex_model.py  
      │  │  │  cnn.py  
      │  │  │  DenseNet.py  
      │  │  │  EffientNet0.py  
      │  │  │  modelFactory.py  
      │  │  │  models.py  
      │  │  │  models_for_U.py  
      │  │  │  model_factory.py  
      │  │  │  resnet.py  
      │  │          
      │  ├─process  
      │  │      baseClient.py  
      │  │      baseClientManager.py  
      │  │      baseServer.py  
      │  │      baseServerManageger.py  
      │  │             
      │  ├─variants  
      │  │  │  variantsFactory.py  
      │  │  │    
      │  │  ├─Asynchronous  
      │  │  │             
      │  │  ├─asyVanilla
      │  │  │  │  client.py  
      │  │  │  │  client_manager.py  
      │  │  │  │  message_define.py  
      │  │  │  │  readme.md  
      │  │  │  │  server.py  
      │  │  │  │  server_manager.py  
      │  │  │  │  __init__.py  
      │  │  │           
      │  │  ├─comp_model   
      │  │  │              
      │  │  ├─fedavg  
      │  │  │  
      │  │  │          
      │  │  ├─parallel_U_Shape   
      │  │  │       
      │  │  ├─SGLR  
      │  │  │         
      │  │  ├─SplitFed  
      │  │  │            
      │  │  ├─SplitFed2  
      │  │  │           
      │  │  ├─synchronization  
      │  │  │           
      │  │  ├─TaskAgnostic  
      │  │  │                 
      │  │  ├─Ushaped  
      │  │  │              
      │  │  ├─vanilla  
      │  │  │              
      │  │  ├─vertical  
      │              
      │            
      ├─data  
      │  ├─adult  
      │  │      adult.data  
      │  │      adult.test  
      │  │      
      │  ├─CheXpert-v1.0-small  
      │  ├─cifar10  
      │  │        
      │  ├─fashionmnist  
      │  │  └─FashionMNIST  
      │  │                
      │  ├─german  
      │  │      german.data-numeric  
      │  │        
      │  └─mnist  
      │      │   
      │      └─MNIST  
      │                     
      ├─model_save  
      │        
      └─Parse  
          │  abstractParse.py  
          │  baseParse.py  
          │  parseFactory.py  
          │  utlis.py  
          │    
          ├─JSON  
          │  │  jsonParse.py  
          │    
          │            
          ├─YAML …… YAML
          │  │  yamlParse.py  
  


## How to Use
After downloading the entire file, it is necessary to configure the relevant environment and install MPI along with the following libraries:
```
yaml
py4mpi
pytorch
scikit-learn
pandas
numpy
pillow
matplotlib
```
To use existing paradigms, only the config.yaml file needs to be configured. Here's an example using PSL as an illustration: 

```
dataDir: ./data/
dataset: mnist
device: cpu
download: true
batch_size: 128
epochs: 15
log_step: 20
lr: 0.01
max_rank: 2
partition_method: homo
variants_type: psl
server_rank: 0


```
Among these parameters, variants_type indicates the type of paradigm, partition_method represents the data set partitioning method, dataset denotes the used dataset, and epochs and batch_size respectively specify the number of training rounds and the batch size per round.

An example of the main function is provided below:
```
if __name__ == '__main__':
    args = parseFactory(fileType=YAML).factory()
    client_model = LeNetClientNetwork()
    
    server_model = LeNetServerNetwork()
    args.load('./config.yaml')

    comm, process_id, worker_number = SplitNN_init(args)
    args["rank"] = process_id  # Set the current process_id.

    args["client_model"] = client_model
    args["server_model"] = server_model
    device = init_training_device(process_id, worker_number - 1, args.gpu_num_per_server)
    args["device"] = device

    dataset = datasetFactory(args).factory()  # loader data and partition method

    train_data_num, train_data_global, test_data_global, local_data_num, \
    train_data_local, test_data_local, class_num = dataset.load_partition_data(process_id) 

    SplitNN_distributed(process_id, args)
```
In the main function, it is necessary to declare the used model.
```
    args["client_model"] = client_model
    args["server_model"] = server_model
```
To execute, input the following command in the command line:
`mpiexec -np N python filename`
Here, N represents the number of processes, equivalent to the number of clients plus one, and 'filename' indicates the name of the file where the main function is located.
## Your Own Paradigm
You can imitate the writing style of your own paradigms. The required files are as follows:
```
client.py  // Defines relevant parameters and training methods for the client
client_manager.py  // Defines methods for client communication
message_define.py  // Defines relevant parameters for communication
server.py  // Defines relevant parameters and training methods for the server
server_manager.py  // Defines methods for server communication
```
You can also inherit relevant classes from the process to use some common methods.




