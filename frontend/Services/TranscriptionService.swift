import Foundation

struct TranscriptionResponse: Decodable {
    let transcription: String
    let feedback: String
}

class TranscriptionService {
    func uploadAudio(fileURL: URL, completion: @escaping (String?, String?) -> Void) {
        guard let url = URL(string: "http://192.168.3.95:5002/upload") else {
            print("Invalid backend URL")
            completion(nil, nil)
            return
        }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        var body = Data()
        let filename = fileURL.lastPathComponent
        let fieldName = "audio"
        let mimeType = "audio/wav"
        if let fileData = try? Data(contentsOf: fileURL) {
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"\(fieldName)\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: \(mimeType)\r\n\r\n".data(using: .utf8)!)
            body.append(fileData)
            body.append("\r\n".data(using: .utf8)!)
            body.append("--\(boundary)--\r\n".data(using: .utf8)!)
            request.httpBody = body
            URLSession.shared.dataTask(with: request) { data, _, error in
                guard let data = data, error == nil else {
                    print("Error sending audio: \(error?.localizedDescription ?? "Unknown error")")
                    completion(nil, nil)
                    return
                }
                do {
                    let decoded = try JSONDecoder().decode(TranscriptionResponse.self, from: data)
                    completion(decoded.transcription, decoded.feedback)
                } catch {
                    print("Error decoding response: \(error)")
                    completion(nil, nil)
                }
            }.resume()
        }
    }
}

