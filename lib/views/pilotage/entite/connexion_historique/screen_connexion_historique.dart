import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ScreenConnexionHistorique extends StatefulWidget {
  const ScreenConnexionHistorique({super.key});

  @override
  State<ScreenConnexionHistorique> createState() => _ScreenConnexionHistoriqueState();
}

class _ScreenConnexionHistoriqueState extends State<ScreenConnexionHistorique> {

  final supabase = Supabase.instance.client;
  List<dynamic> dataHistory = [];
  bool isLoading = false;

  void loadingData() async {
    setState(() {
      isLoading = true;
    });
    String? emailCurrent = supabase.auth.currentUser!.email;
    if (emailCurrent != null ) {
      final List<dynamic> KDataHistorique = await supabase.from('Historiques').select().eq("user",emailCurrent).order("date",ascending: false);
      setState(() {
        dataHistory = KDataHistorique;
      });
    } else {
      setState(() {
        dataHistory = [];
      });
    }
    await Future.delayed(Duration(milliseconds: 100));
    setState(() {
      isLoading = false;
    });
    
  }

  @override
  void initState() {
    loadingData();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return SelectionArea(child: Scaffold(
      body: Padding(
        padding: EdgeInsets.only(top: 16,left: 10),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text("Journal d'activités",style: TextStyle(fontSize: 24,color: Color(0xFF3C3D3F),fontWeight: FontWeight.bold),),
                SizedBox(width: 20,),
                IconButton(padding: EdgeInsets.zero,onPressed: (){ loadingData(); },splashRadius: 20, icon: Icon(Icons.refresh,color: Colors.green,size: 30,))
              ],
            ),
            const SizedBox(height: 5,),
            Expanded(child: isLoading ? loadingWidget () : dataHistory.isEmpty ? initWidget()  : dataTable () ),
            const SizedBox(height: 10,),
          ],
        ),
      ),
    ));
  }

  Widget loadingWidget () {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  Widget initWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Padding(
            padding: EdgeInsets.all(20.0),
            child: Text("Aucune donnée",style:TextStyle(fontSize: 20) ,),
          ),
          const SizedBox(height: 10,),
          IconButton(padding: EdgeInsets.zero,onPressed: (){ loadingData();}, icon: Icon(Icons.refresh,color: Colors.green,size: 40,))
        ],
      ),
    );
  }

  Widget dataTable () {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SingleChildScrollView(
        child: DataTable(
            columnSpacing: 50,
            headingRowHeight: 40,
            headingTextStyle: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            headingRowColor: MaterialStateColor.resolveWith((states) => Colors.blue.withOpacity(0.5)),
            horizontalMargin: 12,
            columns: const [
              DataColumn(label: Text('#')),
              DataColumn(label: Text('Email')),
              DataColumn(label: Text('Action')),
              DataColumn(label: Text('Date & Heure')),
              DataColumn(label: Text('Localisation approximative')),
            ],
            rows: List.generate(
              dataHistory.length, (index) => historiqueDataRow(index),
            )
        ),
      ),
    );
  }

  DataRow historiqueDataRow(int index) {
    return DataRow(
      cells: [
        DataCell(Text("${index+1}",style: TextStyle(fontSize: 20),)),
        DataCell(Text("${dataHistory[index]["user"]}",style: TextStyle(fontSize: 20))),
        DataCell(Text("${dataHistory[index]["action"]}",style: TextStyle(fontSize: 20))),
        DataCell(Text("${formatDate(dataHistory[index]["date"])}",style: TextStyle(fontSize: 20))),
        DataCell(Container(width: 400,child: Text("${dataHistory[index]["localisation"]}",style: TextStyle(fontSize: 20)))),
      ],
    );
  }

  String formatDate(String dateString) {
    final date = DateTime.parse(dateString);
    return "${date.day}/${date.month}/${date.year} - ${date.hour}:${date.month}:${date.second}";
  }

}
