window.addEventListener("load", (event) => {keplrLoad();});

window.addEventListener("keplr_keystorechange", (event) => {keplrLoad();});

async function keplrLoad() {
    if (!window.keplr){
        alert("Please install keplr extension");
    } else {
        const chainId = "kichain-2";

        // Enabling before using the Keplr is recommended.
        // This method will ask the user whether to allow access if they haven't visited this website.
        // Also, it will request that the user unlock the wallet if the wallet is locked.
        await window.keplr.enable(chainId);
    
        const offlineSigner = window.keplr.getOfflineSigner(chainId);
    
        // You can get the address/public keys by `getAccounts` method.
        // It can return the array of address/public key.
        // But, currently, Keplr extension manages only one address/public key pair.
        const accounts = await offlineSigner.getAccounts();
		
		document.getElementById("wallet").innerHTML = accounts[0].address ;		
		
        document.getElementById('get-data').click();
		
		return accounts[0].address;
    }
}

