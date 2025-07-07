Sync Member detail to MyKarya
# i. Desktop need to create folder 'C:\DIVA\MACP_MBR'
# ii. Desktop need to connect to network 'X:\Dist_Reports\Dist_No_Report'
1. Copy all distribution file to 'X:\Dist_Reports\Dist_No_Report\xx' based on the distribution period.
2. Run 'Sync_Mbr_Dtl.py' to start sync member detail and adjustment statement to the 'C:\DIVA\MACP_MBR\*'.
	2.1 input Distribution Period: # e.g., 202503
    2.2 input Distribution directory: # e.g., March 2025 Distribution#
3. Two .bat file will create:
   3.1 202503_mkdir_ipi_fdr.bat --> This bat is create new folder for each involving member for this distribution period
   3.2 202503_from_fdr.bat --> This bat is copy the member detail statement to MyKarya portal, please check cp_dist.log after done.
   3.3 202503_mvdir_ipi_fdr.bat --> This bat is replace the #March 2025 Distribution# to #March_2025_Distribution# to make live in MyKarya portal.
 
