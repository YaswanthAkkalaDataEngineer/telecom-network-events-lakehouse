export type IncidentInput={towerId:string;severity:'LOW'|'MEDIUM'|'HIGH'|'CRITICAL';summary:string};
export function triageNetworkIncident(input:IncidentInput){
 const score={LOW:25,MEDIUM:50,HIGH:75,CRITICAL:100}[input.severity];
 return {towerId:input.towerId,priorityScore:score,escalationRequired:score>=75,recommendedAction:score>=75?'Open a priority ticket and notify network operations.':'Queue for analyst review.'};
}
