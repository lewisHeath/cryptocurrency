import './App.css';
import { useState } from 'react';

function App() {

    const [publicKey, setPublicKey] = useState('');
    const [privateKey, setPrivateKey] = useState('');

    const generateKeys = async () => {
        const response = await fetch('http://localhost:8333/generate_wallet', {
            //add cross origin header to allow fetch to work from different domain
            headers: {
                'Access-Control-Allow-Origin': '*'
            }
        });
        const data = await response.json();
        console.log(data);
        setPublicKey(data.public_key);
        setPrivateKey(data.private_key);
    }

    return (
        <div className="App">
            <h2>wallet generator</h2>
            <div className="wallet">
                <button onClick={generateKeys}>generate</button>
                <h4>public key</h4>
                <p>{publicKey || "click to generate"}</p>
                <h4>private key</h4>
                <p>{privateKey || "click to generate"}</p>
            </div>
        </div>
    );
}

export default App;
