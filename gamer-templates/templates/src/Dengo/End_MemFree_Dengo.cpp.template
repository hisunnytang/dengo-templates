#include "GAMER.h"

#ifdef SUPPORT_DENGO




//-------------------------------------------------------------------------------------------------------
// Function    :  End_MemFree_Dengo
// Description :  Free memory previously allocated by Init_MemAllocate_Dengo()
//
// Note        :  1. Work even when GPU is enabled
//                2. Invoked by End_MemFree()
//
// Parameter   :  None
//-------------------------------------------------------------------------------------------------------
void End_MemFree_Dengo()
{

// nothing to do if Dengo is disabled
   if ( !DENGO_ACTIVATE )   return;


   for (int t=0; t<2; t++)
   {
      if ( h_Che_Array[t] != NULL )    delete [] h_Che_Array[t];
      h_Che_Array[t] = NULL;
   }

} // FUNCTION : End_MemFree_Dengo



#endif // #ifdef SUPPORT_DENGO
