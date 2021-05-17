# glue-catalog-partition-management-parent

   ## Version  -1.0
   Git Repo trigger CICD pipelines for Lambda Code Deployment.

   ## Description:
   Lambda function to extract Tables Information from **RAW databases in Glue Catalog** 
   Also, Trigger Child Lambda function to **Create/Update Partitions** for the extracted Tables.
   This Lambda function will :
   1. fetch all Glue Databases  
   2. Filter RAW databases from the list
   3. Pass on the database information to the child Lambda function to process.
   4. All the child lambdas invoked in an asynchronous invocation. That is, it does not wait for the response back from the child lambdas.
