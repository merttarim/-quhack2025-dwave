import UIKit

class NewTableViewController: UITableViewController, UISearchBarDelegate {

    @IBOutlet weak var firefighterCell: UITableViewCell!
        @IBOutlet weak var policeCell: UITableViewCell!
        @IBOutlet weak var paramedicCell: UITableViewCell!
        
        @IBOutlet weak var firefighterCell1: UITableViewCell!
        @IBOutlet weak var policeCell1: UITableViewCell!
        @IBOutlet weak var paramedicCell1: UITableViewCell!
        
        @IBOutlet weak var firefighterCell2: UITableViewCell!
        @IBOutlet weak var policeCell2: UITableViewCell!
        @IBOutlet weak var paramedicCell2: UITableViewCell!
        
    @IBOutlet weak var firefighterCell3: UITableViewCell!
    @IBOutlet weak var policeCell3: UITableViewCell!
    @IBOutlet weak var paramedicCell3: UITableViewCell!
    
    
        @IBOutlet weak var searchBar: UISearchBar!
        
        // Original cell data
        var allCells: [(cell: UITableViewCell, title: String)] = []
        var filteredCells: [(cell: UITableViewCell, title: String)] = []
        
        override func viewDidLoad() {
            super.viewDidLoad()
            
            searchBar.delegate = self

            
            // Map cells to their titles
            allCells = [
                (firefighterCell, "Firefighter Unit #1"),
                (policeCell, "Firefighter Unit #2"),
                (paramedicCell, "Firefighter Unit #3"),
                (firefighterCell1, "Medical Supplies #1"),
                (policeCell1, "Medical Supplies #2"),
                (paramedicCell1, "Medical Supplies #3"),
                (firefighterCell2, "Emergency Shelter #1"),
                (policeCell2, "Emergency Shelter #2"),
                (paramedicCell2, "Emergency Shelter #3"),
                (firefighterCell3, "Emergency Shelter #4"),
                (policeCell3, "Emergency Shelter #5"),
                (paramedicCell3, "Emergency Shelter #6"),
            
                
            ]


            // Set labels explicitly (optional, for extra safety)
            firefighterCell.textLabel?.text = "Firefighter Unit #1"
            policeCell.textLabel?.text = "Firefighter Unit #2"
            paramedicCell.textLabel?.text = "Firefighter Unit #3"
            firefighterCell1.textLabel?.text = "Medical Supplies #1"
            policeCell1.textLabel?.text = "Medical Supplies #2"
            paramedicCell1.textLabel?.text = "Medical Supplies #3"
            firefighterCell2.textLabel?.text = "Emergency Shelter #1"
            policeCell2.textLabel?.text = "Emergency Shelter #2"
            paramedicCell2.textLabel?.text = "Emergency Shelter #3"
            
            firefighterCell3.textLabel?.text = "Emergency Shelter #4"
            policeCell3.textLabel?.text = "Medical Supplies #4"
            paramedicCell3.textLabel?.text = "Emergency Shelter #5"
            
            
            
            // Default state: show all cells
            filteredCells = allCells
        }
        
        // MARK: - TableView Data Source
        
        override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
            return filteredCells.count
        }

        override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
            return filteredCells[indexPath.row].cell
        }

        // MARK: - SearchBar Filtering
        
        func searchBar(_ searchBar: UISearchBar, textDidChange searchText: String) {
            if searchText.isEmpty {
                filteredCells = allCells
            } else {
                filteredCells = allCells.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
            }
            tableView.reloadData()
        }
    }

